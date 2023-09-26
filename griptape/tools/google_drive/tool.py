from __future__ import annotations
import logging
from schema import Schema, Literal, Optional, Or
from attr import define, field
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, BlobArtifact, TextArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient, BaseTool
from google.auth.exceptions import MalformedError
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from io import BytesIO


@define
class GoogleDriveClient(BaseGoogleClient, BaseTool):
    LIST_FILES_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    UPLOAD_FILE_SCOPES = ['https://www.googleapis.com/auth/drive.file']
    GOOGLE_EXPORT_MIME_MAPPING = {
        "application/vnd.google-apps.document":
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.google-apps.spreadsheet":
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.google-apps.presentation":
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    }

    owner_email: str = field(kw_only=True)

    @activity(config={
        "description": "Can be used to list files in a specific Google Drive folder or the root directory",
        "schema": Schema({
            Literal("folder_path",
                    description="Path of the Google Drive folder (like 'MainFolder/Subfolder1/Subfolder2') "
                                "from which files should be listed. Specify 'root' to list files from the "
                                "root directory."): str,
        })
    })
    def list_files(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES)

            if values["folder_path"] == "root":
                query = "mimeType != 'application/vnd.google-apps.folder' and 'root' in parents and trashed=false"
            else:
                folder_id = self._path_to_file_id(service, values["folder_path"])
                if folder_id:
                    query = f"'{folder_id}' in parents and trashed=false"
                else:
                    return ErrorArtifact(f"Could not find folder: {values['folder_path']}")

            items = self._list_files(service, query)
            return ListArtifact([TextArtifact(i) for i in items])

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving files from Google Drive: {e}")

    @activity(
        config={
            "description": "Can be used to save memory artifacts to Google Drive using folder paths",
            "schema": Schema(
                {
                    "memory_name": str,
                    "artifact_namespace": str,
                    "file_name": str,
                    Optional(
                        "folder_path",
                        description="Path of the Google Drive folder (like 'MainFolder/Subfolder1/Subfolder2') "
                                    "where the file should be saved. Specify 'root' to save in the "
                                    "root directory.",
                        default='root'
                    ): str,
                }
            ),
        }
    )
    def save_memory_artifacts_to_drive(self, params: dict) -> ErrorArtifact | InfoArtifact:
        values = params["values"]
        memory = self.find_input_memory(values["memory_name"])
        file_name = values["file_name"]

        if memory:
            artifacts = memory.load_artifacts(values["artifact_namespace"])

            if artifacts:
                service = self._build_client(self.UPLOAD_FILE_SCOPES)

                if values["folder_path"] == "root":
                    folder_id = "root"
                else:
                    folder_id = self._path_to_file_id(service, values["folder_path"])

                if folder_id:
                    try:
                        if len(artifacts) == 1:
                            self._save_to_drive(file_name, artifacts[0].value, folder_id)
                        else:
                            for a in artifacts:
                                self._save_to_drive(f"{a.name}-{file_name}", a.value, folder_id)

                        return InfoArtifact(f"saved successfully")

                    except Exception as e:
                        return ErrorArtifact(f"error saving file to Google Drive: {e}")
                else:
                    return ErrorArtifact(f"Could not find folder: {values['folder_path']}")
            else:
                return ErrorArtifact("no artifacts found")
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to save content to a file on Google Drive",
        "schema": Schema(
            {
                Literal(
                    "path",
                    description="Destination file path on Google Drive in the POSIX format. "
                                "For example, 'foo/bar/baz.txt'"
                ): str,
                "content": str
            }
        )
    })
    def save_content_to_drive(self, params: dict) -> ErrorArtifact | InfoArtifact:
        content = params["values"]["content"]
        filename = params["values"]["path"]

        try:
            self._save_to_drive(filename, content)

            return InfoArtifact(f"saved successfully")
        except Exception as e:
            return ErrorArtifact(f"error saving file to Google Drive: {e}")

    @activity(config={
        "description": "Can be used to download multiple files from Google Drive based on a provided list of paths",
        "schema": Schema({
            Literal(
                "paths",
                description="List of paths to files to be loaded in the POSIX format. "
                            "For example, ['foo/bar/file1.txt', 'foo/bar/file2.txt']"
            ): [str]
        })
    })
    def download_files(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]
        downloaded_files = []
    
        service = self._build_client(self.LIST_FILES_SCOPES)
    
        for path in values["paths"]:
            try:
                file_id = self._path_to_file_id(service, path)
                if file_id:
                    file_info = service.files().get(fileId=file_id).execute()
                    mime_type = file_info["mimeType"]
    
                    if mime_type in self.GOOGLE_EXPORT_MIME_MAPPING:
                        export_mime = self.GOOGLE_EXPORT_MIME_MAPPING[mime_type]
                        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
                    else:
                        request = service.files().get_media(fileId=file_id)
    
                    downloaded_file = request.execute()
                    logging.info(f"File '{path}' successfully downloaded.")
                    downloaded_files.append(BlobArtifact(downloaded_file))
                else:
                    logging.error(f"Could not find file: {path}")
                    downloaded_files.append(
                        ErrorArtifact(f"Could not find file: {path}")
                    )
    
            except HttpError as e:
                logging.error(e)
                downloaded_files.append(
                    ErrorArtifact(f"error downloading file '{path}' from Google Drive: {e}")
                )
            except MalformedError:
                logging.error("MalformedError occurred")
                downloaded_files.append(
                    ErrorArtifact(f"error downloading file '{path}' from Google Drive due to malformed credentials")
                )
    
        return ListArtifact(downloaded_files)

    @activity(
        config={
            "description": "Can search for files on Google Drive based on name or content",
            "schema": Schema(
                {
                    Literal(
                        "search_mode",
                        description="File search mode. Use 'name' to search in file name or "
                                    "'content' to search in file content",
                    ): Or("name", "content"),
                    Literal(
                        "search_query",
                        description="Query to search for. If search_mode is 'name', it's the file name. If 'content', "
                        "it's the text within files.",
                    ): str,
                    Literal(
                        "folder_path",
                        description="Path of the Google Drive folder (like 'MainFolder/Subfolder1/Subfolder2') "
                        "where the search should be performed. Specify 'root' to search in the "
                        "root directory.",
                    ): str,
                }
            ),
        }
    )
    def search_files(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]
    
        search_mode = values["search_mode"]
    
        try:
            service = self._build_client(self.LIST_FILES_SCOPES)
    
            folder_id = None
            if values["folder_path"] == "root":
                folder_id = "root"
            else:
                folder_id = self._path_to_file_id(service, values["folder_path"])
    
            if folder_id:
                query = None
                if search_mode == "name":
                    query = f"name='{values['search_query']}'"
                elif search_mode == "content":
                    query = f"fullText contains '{values['search_query']}'"
    
                query += " and trashed=false"
                if folder_id != "root":
                    query += f" and '{folder_id}' in parents"
    
                results = service.files().list(q=query).execute()
                items = results.get("files", [])
                return ListArtifact([TextArtifact(i) for i in items])
            else:
                return ErrorArtifact(f"Folder path {values['folder_path']} not found")
    
        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error searching for file in Google Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error searching for file due to malformed credentials")

    def _build_client(self, scopes: list[str]) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )

        return build(
            serviceName="drive",
            version="v3",
            credentials=credentials.with_subject(self.owner_email)
        )

    def _path_to_file_id(self, service, path: str) -> Optional[str]:
        parts = path.split("/")
        current_id = "root"
    
        for idx, part in enumerate(parts):
            if idx == len(parts) - 1:  # If it's the last part
                query = f"name='{part}' and '{current_id}' in parents"  # No mime type restriction
            else:
                query = f"name='{part}' and '{current_id}' in parents and mimeType='application/vnd.google-apps.folder'"
    
            response = service.files().list(q=query).execute()
            files = response.get("files", [])
    
            if not files and idx != len(parts) - 1:  # Only create folders for non-last parts
                folder_metadata = {"name": part, "mimeType": "application/vnd.google-apps.folder", "parents": [current_id]}
                folder = service.files().create(body=folder_metadata, fields="id").execute()
                current_id = folder.get("id")
            elif files:
                current_id = files[0]["id"]
            else:
                return None  # File not found
    
        return current_id

    def _save_to_drive(self, filename: str, value: any, parent_folder_id=None) -> InfoArtifact | ErrorArtifact:
        service = self._build_client(self.UPLOAD_FILE_SCOPES)
    
        if isinstance(value, str):
            value = value.encode()

        parts = filename.split("/")
        if len(parts) > 1:
            directory = "/".join(parts[:-1])
            parent_folder_id = self._path_to_file_id(service, directory)
            if not parent_folder_id:
                return ErrorArtifact(f"Could not find folder: {directory}")
            filename = parts[-1]
    
        file_metadata = {"name": filename}
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]
    
        media = MediaIoBaseUpload(BytesIO(value), mimetype="application/octet-stream", resumable=True)

        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return InfoArtifact(file)

    def _list_files(self, service, query: str) -> list:
        items = []
        next_page_token = None
    
        while True:
            results = (
                service.files()
                .list(
                    q=query,
                    pageToken=next_page_token,
                )
                .execute()
            )
    
            files = results.get("files", [])
            items.extend(files)
    
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break
    
        return items
