import os, pyrebase
from secrets import token_hex
from fastapi import HTTPException, UploadFile, status

from api.core.dependencies.firebase_config import firebase_config
from api.utils.settings import settings


class FirebaseService:
    
    @classmethod
    async def upload_file(
        cls, 
        file, 
        allowed_extensions: list | None, 
        upload_folder: str, 
        model_id: str
    ):
        '''Function to upload a file'''
        
        # Check against invalid extensions
        file_name = file.filename.lower()
        
        file_extension = file_name.split('.')[-1]
        name = file_name.split('.')[0]
        
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File cannot be blank')
        
        if allowed_extensions:
            if file_extension not in allowed_extensions:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format')
        
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        
        # Generate a new file name
        new_filename = f'{name}-{token_hex(5)}.jpg'
        
        # Save file temporarily
        save_path = os.path.join(settings.TEMP_DIR, new_filename)
        
        with open(save_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Initailize firebase
        firebase = pyrebase.initialize_app(firebase_config)
        
        # Set up storage and a storage path for each file
        storage = firebase.storage()
        firebase_storage_path = f'rescue-radar/{upload_folder}/{model_id}/{new_filename}'
        
        # Store the file in the firebase storage path
        storage.child(firebase_storage_path).put(save_path)
        
        # Get download URL
        download_url = storage.child(firebase_storage_path).get_url(None)
        
        # Delete the temporary file
        os.remove(save_path)
        
        return download_url
        
        # return {
        #     'file_name': new_filename,
        #     'download_url': download_url
        # } 
        