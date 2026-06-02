from database.session import get_db
from core.security import oauth2_scheme, decode_access_token
from repositories import users as user_repo 
from fastapi import HTTPException, Depends, status 
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(db: AsyncSession = Depends(get_db) ,token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token missing subject",
                            headers={"WWW-Authenticate" :"Bearer"}
                            )
 
    user = await user_repo.get_by_field_or_404(db = db, field = user_repo.UserLookupField.EMAIL, value = email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    return user    