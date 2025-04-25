from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db, User, UserType
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter()

class UserTypeEnum(str, Enum):
    SUPERADMIN = "超级管理员"
    PROJECT_ADMIN = "项目管理员"
    REGULAR = "普通用户"

class UserBase(BaseModel):
    name: str
    email: str
    tenant: str
    department: str
    project: str
    role: str
    user_type: UserTypeEnum = UserTypeEnum.REGULAR
    tabs_accepted: int
    premium_requests_used: int

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    
    class Config:
        orm_mode = True

def get_current_user(current_user_id: Optional[int] = Header(None, alias="user-id"), db: Session = Depends(get_db)):
    if current_user_id is None:
        return None
    
    user = db.query(User).filter(User.id == current_user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def check_admin_permission(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.user_type not in [UserType.SUPERADMIN, UserType.PROJECT_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    return current_user

def check_superadmin_permission(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.user_type != UserType.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Super admin permission required")
    
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        users = db.query(User).filter(User.user_type == UserType.REGULAR).all()
    elif current_user.user_type == UserType.SUPERADMIN:
        users = db.query(User).all()
    elif current_user.user_type == UserType.PROJECT_ADMIN:
        users = db.query(User).filter(
            (User.project == current_user.project) | 
            (User.user_type == UserType.SUPERADMIN)
        ).all()
    else:
        users = [current_user]
    
    return users

@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin_permission)
):
    if user.user_type != UserTypeEnum.REGULAR and current_user.user_type != UserType.SUPERADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Only super admins can create admin users"
        )
    
    if (current_user.user_type == UserType.PROJECT_ADMIN and 
        user.project != current_user.project):
        raise HTTPException(
            status_code=403, 
            detail="Project admins can only create users in their own project"
        )
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user is None:
        if db_user.user_type != UserType.REGULAR:
            raise HTTPException(status_code=403, detail="Permission denied")
    elif current_user.user_type == UserType.PROJECT_ADMIN:
        if db_user.project != current_user.project and db_user.user_type != UserType.SUPERADMIN:
            raise HTTPException(status_code=403, detail="Permission denied")
    elif current_user.user_type == UserType.REGULAR:
        if db_user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Permission denied")
    
    return db_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.user_type != UserType.REGULAR and current_user.user_type != UserType.SUPERADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Only super admins can update admin users"
        )
    
    if (current_user.user_type == UserType.PROJECT_ADMIN and 
        db_user.project != current_user.project):
        raise HTTPException(
            status_code=403, 
            detail="Project admins can only update users in their own project"
        )
    
    if user.user_type != db_user.user_type and current_user.user_type != UserType.SUPERADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Only super admins can change user types"
        )
    
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.user_type != UserType.REGULAR and current_user.user_type != UserType.SUPERADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Only super admins can delete admin users"
        )
    
    if (current_user.user_type == UserType.PROJECT_ADMIN and 
        db_user.project != current_user.project):
        raise HTTPException(
            status_code=403, 
            detail="Project admins can only delete users in their own project"
        )
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
