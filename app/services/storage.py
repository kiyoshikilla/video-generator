import os
import shutil
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import timedelta
from google.cloud import storage

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

class GCSStorage(StorageInterface):
    def __init__(self, bucket_name: str, credentials_path: str):
        self.client = storage.Client.from_service_account_json(credentials_path)
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)

    def upload(self, file_path: Path, destination_folder: str) -> str:
        blob_name = f"{destination_folder}/{file_path.name}"
        blob = self.bucket.blob(blob_name)

        print(f"Uploading to Google Cloud Bucket: {blob_name}")
        
        blob.upload_from_filename(str(file_path))

        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )

class CombinedStorage(StorageInterface):
    def __init__(self, local: LocalStorage, gcs: GCSStorage):
        self.local = local
        self.gcs = gcs

    def upload(self, file_path: Path, destination_folder: str) -> str:
        self.local.upload(file_path, destination_folder)
        return self.gcs.upload(file_path, destination_folder)

def get_storage() -> StorageInterface:
    storage_type = os.getenv("STORAGE_TYPE", "LOCAL")

    key_path = os.getenv("GOOGLE_KEY")
    bucket_name = os.getenv("GCS_BUCKET_NAME")

    if storage_type == "GCS":
        if not bucket_name: raise ValueError("GCS_BUCKET_NAME missing")
        return GCSStorage(bucket_name, key_path)
    
    elif storage_type == "HYBRID_GCS":
        if not bucket_name: raise ValueError("GCS_BUCKET_NAME missing")
        return CombinedStorage(
            local=LocalStorage(),
            gcs=GCSStorage(bucket_name, key_path)
        )
    
    return LocalStorage()