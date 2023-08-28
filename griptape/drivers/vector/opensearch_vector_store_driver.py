from typing import Optional, Union, Tuple
from opensearchpy import OpenSearch, RequestsHttpConnection
from griptape import utils
import logging
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field, Factory
logging.basicConfig(level=logging.ERROR)


@define
class OpenSearchVectorStoreDriver(BaseVectorStoreDriver):
    host: str = field(kw_only=True)
    port: int = field(default=443, kw_only=True)
    http_auth: Optional[Union[str, Tuple[str, str]]] = field(default=None, kw_only=True)
    use_ssl: bool = field(default=True, kw_only=True)
    verify_certs: bool = field(default=True, kw_only=True)
    index_name: str = field(kw_only=True)

    client: OpenSearch = field(default=Factory(
        lambda self: OpenSearch(
            hosts=[{'host': self.host, 'port': self.port}],
            http_auth=self.http_auth,
            use_ssl=self.use_ssl,
            verify_certs=self.verify_certs,
            connection_class=RequestsHttpConnection
        ),
        takes_self=True
    ))

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:

        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
        doc = {
            "vector": vector,
            "namespace": namespace,
            "metadata": meta
        }
        doc.update(kwargs)
        response = self.client.index(index=self.index_name, id=vector_id, body=doc,
                                     routing=namespace if namespace else "default")

        return response["_id"]

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        try:
            response = self.client.get(index=self.index_name, id=vector_id, routing=namespace if namespace else None)
            if response["found"]:
                vector_data = response["_source"]
                if namespace and vector_data.get("namespace") != namespace:
                    # Entry doesn't belong to the specified namespace
                    return None
                entry = BaseVectorStoreDriver.Entry(
                    id=vector_id,
                    meta=vector_data.get("metadata"),
                    vector=vector_data.get("vector"),
                    namespace=vector_data.get("namespace")
                )
                return entry
            else:
                return None
        except Exception as e:
            logging.error(f"Error while loading entry: {e}")
            return None

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:

        query_body = {
            "size": 10000,
            "query": {
                "match_all": {}
            }
        }

        # If a namespace is provided, adjust the query to match vectors in that namespace
        if namespace:
            query_body["query"] = {
                "match": {
                    "namespace": namespace
                }
            }

        response = self.client.search(index=self.index_name, body=query_body, routing=namespace if namespace else None)

        entries = []
        for hit in response["hits"]["hits"]:
            vector_data = hit["_source"]
            entry = BaseVectorStoreDriver.Entry(
                id=hit["_id"],
                vector=vector_data.get("vector"),
                meta=vector_data.get("metadata"),
                namespace=vector_data.get("namespace")
            )
            entries.append(entry)
        return entries

    def query(
            self,
            query: str,
            count: Optional[int] = None,
            field_name: str = "vector",
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            include_metadata=True,
            **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        count = count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT
        vector = self.embedding_driver.embed_string(query)
        # Base k-NN query
        query_body = {
            "size": count,
            "query": {
                "knn": {
                    field_name: {
                        "vector": vector,
                        "k": count
                    }
                }
            }
        }

        # If a namespace is provided, adjust the query to match vectors in that namespace
        if namespace:
            query_body["query"] = {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "namespace": namespace
                            }
                        },
                        {
                            "knn": {
                                field_name: {
                                    "vector": vector,
                                    "k": count
                                }
                            }
                        }
                    ]
                }
            }

        response = self.client.search(index=self.index_name, body=query_body)

        return [
            BaseVectorStoreDriver.QueryResult(
                namespace=hit["_source"].get("namespace") if namespace else None,
                score=hit["_score"],
                vector=hit["_source"].get("vector") if include_vectors else None,
                meta=hit["_source"].get("metadata") if include_metadata else None
            )
            for hit in response["hits"]["hits"]
        ]

    def create_index(self, vector_dimension):
        if not self.client.indices.exists(index=self.index_name):
            mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index.knn": True
                },
                "mappings": {
                    "properties": {
                        "vector": {
                            "type": "knn_vector",
                            "dimension": vector_dimension
                        },
                        "namespace": {
                            "type": "keyword"
                        },
                        "metadata": {
                            "type": "object",
                            "enabled": True
                        }
                    }
                }
            }
            try:
                self.client.indices.create(index=self.index_name, body=mapping)
            except Exception as e:
                logging.error(f"Error initializing the index: {e}")
