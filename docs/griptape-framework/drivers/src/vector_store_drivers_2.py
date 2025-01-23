import os

from griptape.drivers.vector.griptape_cloud import GriptapeCloudVectorStoreDriver

# Initialize environment variables
gt_cloud_api_key = os.environ["GT_CLOUD_API_KEY"]
gt_cloud_knowledge_base_id = os.environ["GT_CLOUD_KB_ID"]

vector_store_driver = GriptapeCloudVectorStoreDriver(
    api_key=gt_cloud_api_key, knowledge_base_id=gt_cloud_knowledge_base_id
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
