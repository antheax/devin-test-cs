from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db, Tenant, User, UserType
from pydantic import BaseModel

router = APIRouter()

class TenantBase(BaseModel):
    name: str
    update_cycle: int

class TenantCreate(TenantBase):
    pass

class TenantUpdate(TenantBase):
    pass

class TenantResponse(TenantBase):
    id: int
    
    class Config:
        orm_mode = True

def get_current_user(user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def check_superadmin_permission(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.user_type != UserType.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Super admin permission required")
    
    return current_user

@router.get("/tenants", response_model=List[TenantResponse])
def get_tenants(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None or current_user.user_type != UserType.SUPERADMIN:
        if current_user:
            tenant = db.query(Tenant).filter(Tenant.name == current_user.tenant).first()
            return [tenant] if tenant else []
        return []
    
    tenants = db.query(Tenant).all()
    return tenants

@router.post("/tenants", response_model=TenantResponse)
def create_tenant(
    tenant: TenantCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_superadmin_permission)
):
    existing_tenant = db.query(Tenant).filter(Tenant.name == tenant.name).first()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Tenant with this name already exists")
    
    db_tenant = Tenant(**tenant.dict())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if db_tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if current_user and current_user.user_type != UserType.SUPERADMIN:
        if db_tenant.name != current_user.tenant:
            raise HTTPException(status_code=403, detail="Permission denied")
    
    return db_tenant

@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int, 
    tenant: TenantUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_superadmin_permission)
):
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if db_tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant.name != db_tenant.name:
        existing_tenant = db.query(Tenant).filter(Tenant.name == tenant.name).first()
        if existing_tenant:
            raise HTTPException(status_code=400, detail="Tenant with this name already exists")
    
    for key, value in tenant.dict().items():
        setattr(db_tenant, key, value)
    
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

@router.delete("/tenants/{tenant_id}")
def delete_tenant(
    tenant_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_superadmin_permission)
):
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if db_tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    users_count = db.query(User).filter(User.tenant == db_tenant.name).count()
    if users_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete tenant with {users_count} associated users. Please reassign or delete these users first."
        )
    
    db.delete(db_tenant)
    db.commit()
    return {"message": "Tenant deleted successfully"}
