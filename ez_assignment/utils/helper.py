from django.conf import settings
import os
from django.core.signing import Signer
import uuid

def generate_secure_download_url(file_obj, user):
    signer = Signer()
    
    signed_data = f"{file_obj.pk}:{user.pk}"
    signed_url = signer.sign(signed_data)
    
    return signed_url

def generate_signup_token():
    signer = Signer()
    token = str(uuid.uuid4())
    signed_token = signer.sign(token)
    
    return signed_token

def get_file_type(filename):
    extension = os.path.splitext(filename)[-1].lower()
    
    # Define a mapping of file extensions to file types
    file_type_mapping = {
        '.pptx': 'PPTX',
        '.docx': 'DOCX',
        '.xlsx': 'XLSX',
    }
    
    # Use the mapping to determine the file type, defaulting to 'Unknown' if not found
    return file_type_mapping.get(extension, None)