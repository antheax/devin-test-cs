from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db, Application, User, TargetProduct, ApplicationStatus, UserType
from pydantic import BaseModel, validator
from datetime import date, datetime
from enum import Enum
from .users import get_current_user, check_admin_permission

router = APIRouter()

class TargetProductEnum(str, Enum):
    C = "C"
    W = "W"

class ApplicationStatusEnum(str, Enum):
    PENDING = "申请中"
    COMPLETED = "已完成"

class ApplicationBase(BaseModel):
    application_date: date
    target_product: TargetProductEnum
    status: ApplicationStatusEnum
    user_id: int

    @validator('target_product')
    def validate_target_product(cls, v):
        if v not in [TargetProductEnum.C, TargetProductEnum.W]:
            raise ValueError('Target product must be either C or W')
        return v

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: int
    user_name: Optional[str] = None
    project: Optional[str] = None  # Add project field

    class Config:
        orm_mode = True

@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(month: Optional[str] = None, project: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)

    if month:
        try:
            year_str, month_str = month.split('-')
            year = int(year_str)
            month_num = int(month_str)
            start_date = date(year, month_num, 1)

            if month_num == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month_num + 1, 1)

            query = query.filter(
                Application.application_date >= start_date,
                Application.application_date < end_date
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
            
    if project:
        query = query.join(User).filter(User.project == project)

    applications = query.all()

    result = []
    for app in applications:
        user = db.query(User).filter(User.id == app.user_id).first()
        app_dict = {
            "id": app.id,
            "application_date": app.application_date,
            "target_product": app.target_product,
            "status": app.status,
            "user_id": app.user_id,
            "user_name": user.name if user else None,
            "project": user.project if user else None  # Add project field
        }
        result.append(app_dict)

    return result

@router.post("/applications", response_model=ApplicationResponse)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == application.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_application = Application(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    response = db_application.__dict__.copy()
    response["user_name"] = user.name

    return response

@router.put("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(application_id: int, application: ApplicationCreate, db: Session = Depends(get_db)):
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    user = db.query(User).filter(User.id == application.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in application.dict().items():
        setattr(db_application, key, value)

    db.commit()
    db.refresh(db_application)

    response = db_application.__dict__.copy()
    response["user_name"] = user.name

    return response

@router.delete("/applications/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(db_application)
    db.commit()
    return {"message": "Application deleted successfully"}
