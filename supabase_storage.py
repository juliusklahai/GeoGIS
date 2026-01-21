import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseStorage:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            self.client: Client = create_client(url, key)
        else:
            self.client = None

    def upload_raster(self, bucket: str, path: str, file_path: str):
        """
        Uploads a file to Supabase Storage.
        """
        if not self.client:
            print("Supabase client not initialized. Check ENV variables.")
            return None
            
        with open(file_path, 'rb') as f:
            self.client.storage.from_(bucket).upload(path, f)
            
        return self.client.storage.from_(bucket).get_public_url(path)

    def get_url(self, bucket: str, path: str):
        if not self.client:
            return None
        return self.client.storage.from_(bucket).get_public_url(path)

storage = SupabaseStorage()
