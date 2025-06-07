import os
from PIL import Image

# This path points to the persistent volume inside the container
UPLOAD_DIR = "/app/data/uploads/"
THUMBNAIL_DIR = "/app/data/thumbnails/"

def setup_directories():
    """Ensure upload and thumbnail directories exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    """Saves the uploaded file and creates a thumbnail."""
    setup_directories()
    
    # Save original file
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Create and save thumbnail
    thumb_path = os.path.join(THUMBNAIL_DIR, uploaded_file.name)
    with Image.open(file_path) as img:
        img.thumbnail((128, 128))
        img.save(thumb_path)
        
    return file_path, thumb_path 