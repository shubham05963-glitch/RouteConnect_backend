from collections.abc import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth as firebase_auth
from google.cloud.firestore import Client

from app.core.security import decode_access_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Client = Depends(get_db)):
    subject = decode_access_token(token)
    uid = None
    if not subject:
        try:
            decoded = firebase_auth.verify_id_token(token)
            subject = decoded.get("email")
            uid = decoded.get("uid")
        except Exception:
            subject = None

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    docs = list(db.collection('users').where("email", "==", subject).stream())
    if not docs and uid:
        docs = list(db.collection('users').where("uid", "==", uid).stream())
    if not docs:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = docs[0].to_dict()
    user["doc_id"] = docs[0].id
    # Simple active check fallback
    if user.get("is_active") is False or user.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user


def require_roles(*allowed_roles: str) -> Callable:
    allowed = {r.strip().lower() for r in allowed_roles if r.strip()}

    def _dependency(user=Depends(get_current_user)):
        role = str(user.get("role", "")).lower()
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return user

    return _dependency
