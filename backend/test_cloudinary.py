import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

env_path = r"c:\Users\ashwi\Downloads\Project-Chakravyuh-rebuilt\Project-Chakravyuh-rebuilt\Project-Chakravyuh-Prototype\backend\.env"
load_dotenv(env_path)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# 1x1 transparent PNG
test_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

print("Attempting upload...")
try:
    response = cloudinary.uploader.upload(
        test_base64,
        folder="Project_Chakravyuh/Test_Folder",
        resource_type="image",
        unique_filename=True
    )
    print("Success!", response.get("secure_url"))
except Exception as e:
    print("Failed!", str(e))
