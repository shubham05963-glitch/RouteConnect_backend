from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Client = Depends(get_db)):
    docs = list(db.collection('users').where("email", "==", user_in.email).stream())
    if docs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    doc_ref = db.collection('users').document()
    user_data = {
        "email": user_in.email,
        "hashed_password": get_password_hash(user_in.password),
        "is_active": True
    }
    doc_ref.set(user_data)
    
    return {"id": sum(ord(ch) for ch in doc_ref.id), "email": user_in.email, "is_active": True}


@router.post("/login", response_model=Token)
def login(form_data: LoginRequest, db: Client = Depends(get_db)):
    docs = list(db.collection('users').where("email", "==", form_data.email).stream())
    if not docs:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    user = docs[0].to_dict()
    if not verify_password(form_data.password, user.get("hashed_password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token(subject=user["email"])
    return {"access_token": token, "token_type": "bearer"}
