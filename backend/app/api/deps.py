from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import oauth2_scheme, decode_access_token
from app.database.session import AsyncSessionLocal
from app.repositories import user as user_repo


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_from_token(db: AsyncSession, token: str):
    payload = decode_access_token(token)
    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token missing subject",
                            headers={"WWW-Authenticate" :"Bearer"}
                            )
 
    user = await user_repo.get_user_by_email(db=db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    return user    


async def get_current_user(db: AsyncSession = Depends(get_db) ,token: str = Depends(oauth2_scheme)):
    return await get_user_from_token(db=db, token=token)
