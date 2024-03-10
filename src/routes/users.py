import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.database.models import User
from src.services.auth import auth_service
from src.schemas import UserDb
from src.database.db import get_db
from src.conf.config import settings
from src.repository import users as repositories_users


router = APIRouter(prefix='/users', tags=['users'])

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


@router.get('/me', response_model=UserDb)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):

    public_id = f'FastApiApp/{user.email}'
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=res.get('version'))

    user =  await repositories_users.update_avatar_url(user.email, res_url, db)

    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    
    return user