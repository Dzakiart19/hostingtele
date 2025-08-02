import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import unquote

import httpx
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db, User


security = HTTPBearer()


def verify_telegram_auth(auth_data: Dict[str, Any]) -> bool:
    """
    Verifikasi otentikasi Telegram Login Widget
    """
    check_hash = auth_data.pop('hash', '')
    
    # Buat string data terurut
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        data_check_arr.append(f"{key}={value}")
    data_check_string = '\n'.join(data_check_arr)
    
    # Buat secret key dari bot token
    secret_key = hashlib.sha256(settings.platform_bot_token.encode()).digest()
    
    # Hitung hash yang diharapkan
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Verifikasi hash dan waktu
    auth_date = int(auth_data.get('auth_date', 0))
    current_time = int(datetime.now().timestamp())
    
    # Validasi hash dan waktu (maksimal 1 jam)
    return (
        hmac.compare_digest(expected_hash, check_hash) and
        current_time - auth_date <= 3600
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Membuat JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifikasi JWT token
    """
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret, 
            algorithms=["HS256"]
        )
        telegram_id: int = payload.get("telegram_id")
        if telegram_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return telegram_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    telegram_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Mendapatkan user saat ini dari database
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def verify_telegram_bot_token(bot_token: str) -> bool:
    """
    Verifikasi apakah bot token valid dengan memanggil Telegram API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            return response.status_code == 200 and response.json().get("ok", False)
    except:
        return False