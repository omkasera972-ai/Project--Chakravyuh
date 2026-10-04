import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image(file_data, folder_path: str) -> str:
    """
    Uploads an image to Cloudinary in a specific folder.
    
    :param file_data: The file byte stream or base64 data URI.
    :param folder_path: The exact Cloudinary folder path to use.
    :return: The secure URL of the uploaded image.
    """
    try:
        response = cloudinary.uploader.upload(
            file_data,
            folder=folder_path,
            resource_type="image",
            unique_filename=True
        )
        return response.get("secure_url")
    except Exception as e:
        # Do not log the raw exception as it might expose API secrets in Cloudinary auth errors
        print("Error uploading image to Cloudinary (details masked for security).")
        return None
