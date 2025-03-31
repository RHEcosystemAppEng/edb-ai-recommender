from dataclasses import dataclass
import os
import streamlit

@dataclass
class S3ConnectionProfile:
   endpoint_url: str
   bucket_name: str
   region: str
   skip_signature: str
   access_key:str
   secret_key:str
   recommender_images_path:str

def get_s3_connection_profile() -> S3ConnectionProfile:
   
   result = S3ConnectionProfile(os.getenv("S3_ENDPOINT_URL"), os.getenv("S3_BUCKET_NAME"), os.getenv('S3_REGION'), os.getenv("S3_SKIP_SIGNATURE",),
                                os.getenv("S3_ACCESS_KEY"), os.getenv("S3_SECRET_KEY"), os.getenv("S3_RECOMMENDER_IMAGES_PATH"))

   return result
