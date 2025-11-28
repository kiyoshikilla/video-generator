import os 
import shutil
import mimetypes
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


DRIVE_SCOPE = ['https://www.googleapis.com/auth/drive']


class StorageInterface(ABC):
    @abstractmethod
    def upload(self, file_path: Path, destination_folder: str) -> str:
        pass


class LocalStorage(StorageInterface):
    def __init__(self, base_dir: str = "media_output"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)


    def upload(self, file_path: Path, destination_folder: str) -> str:
        
        target_dir = self.base_dir / destination_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        destination = target_dir / file_path.name 
        shutil.copy2(file_path, destination)

        print(f"Saved locally to: {destination}")
        return str(destination.absolute())
    

class GoogleDriveStorage(StorageInterface):
    def __init__(self, drive_placeholder: str, credentials_path: str):
        
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, 
            scopes=DRIVE_SCOPE
        )
        self.service = build('drive', 'v3', credentials=creds)
        
    def _get_or_create_folder(self, folder_name: str) -> str:
        
        query = (
            f"mimeType='application/vnd.google-apps.folder' and "
            f"name='{folder_name}' and trashed=false"
        )
        response = self.service.files().list(q=query, fields='files(id)').execute()
        files = response.get('files', [])

        if files:
            return files[0]['id']
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        print(f"Created Drive folder: {folder_name}")
        return folder.get('id')
        
    def upload(self, file_path: Path, destination_folder: str) -> str:
        
        folder_id = self._get_or_create_folder(destination_folder)

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type: mime_type = 'application/octet-stream'

        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(str(file_path), mimetype=mime_type)
        
        print(f"Uploading into Google Drive: {file_path.name}")
        uploaded_file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='webViewLink'
        ).execute()

        return uploaded_file.get('webViewLink')


class CombinedStorage(StorageInterface):
    def __init__(self, local: LocalStorage, drive: GoogleDriveStorage):
            self.local = local
            self.drive = drive
        
        
    def upload(self, file_path: Path, destination_folder: str) -> str: 
        
        self.local.upload(file_path, destination_folder)
        drive_link = self.drive.upload(file_path, destination_folder)

        return drive_link


def get_storage() -> StorageInterface:
    storage_type = os.getenv("STORAGE_TYPE", "LOCAL")

    key_path = os.getenv("GOOGLE_KEY")
    DRIVE_PLACEHOLDER = "DRIVE_API_IGNORES_THIS"
    
    if storage_type == "DRIVE":
        if not key_path: raise ValueError("GOOGLE_KEY is missing for DRIVE mode")
        return GoogleDriveStorage(DRIVE_PLACEHOLDER, key_path)
    
    elif storage_type == "HYBRID_DRIVE":
        if not key_path: raise ValueError("GOOGLE_KEY is missing for HYBRID_DRIVE mode")
        return CombinedStorage(
            local=LocalStorage(),
            drive=GoogleDriveStorage(DRIVE_PLACEHOLDER, key_path),
        ) 
    return LocalStorage()