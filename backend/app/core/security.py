from typing import Optional 

import jwt 
from jwt.exceptions import InvalidTokenError

from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from fastapi import status, HTTPException

from datetime import datetime, timedelta, timezone

from app.core.config import Settings

password_hash = PasswordHash.recommended()

#Password Hashing

def hash_password(plaintext:str)->str:
    return password_hash.hash(plaintext)

def verify_hashed_password(plaintext:str, hashed_password:str)->bool:
    return password_hash.verify(plaintext,hashed_password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#JWT creation

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=Settings.TOKEN_EXPIRY_IN_MIN)
    )
    payload = {
        "sub":subject,
        "exp":expire,
        "iat":datetime.now(timezone.utc)
    }

    token = jwt.encode(
        payload, algorithm=Settings.HASHING_ALGORITHM, key=Settings.JWT_SECRET
    )
    return token


#JWT verfication

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, key=Settings.JWT_SECRET, algorithms=[Settings.HASHING_ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(
           status_code = status.HTTP_401_UNAUTHORIZED,
           detail = "Could not verify credentials",
           headers ={"WWW-Authenticate":"Bearer"}
        )    
