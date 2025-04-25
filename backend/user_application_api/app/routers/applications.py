from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_db, Application, User, TargetProduct, ApplicationStatus, UserType
from pydantic import BaseModel, validator
from datetime import date, datetime
from enum import Enum
from .users import get_current_user, check_admin_permission
import pandas as pd
import io
from fastapi.responses import StreamingResponse

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

    class Config:
        orm_mode = True

@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(month: Optional[str] = None, db: Session = Depends(get_db)):
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
            "user_name": user.name if user else None
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

@router.post("/applications/batch-import", response_model=Dict[str, int])
async def batch_import_applications(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: Optional[str] = Header(None)
):
    """
    Batch import applications from Excel or CSV file
    """
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Only .xlsx and .csv files are supported")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        else:  # CSV
            df = pd.read_csv(io.BytesIO(contents))
        
        required_columns = ['application_date', 'user_id', 'target_product', 'status']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        imported_count = 0
        for _, row in df.iterrows():
            try:
                app_date = row['application_date']
                if isinstance(app_date, str):
                    app_date = datetime.strptime(app_date, '%Y-%m-%d').date()
                
                user = db.query(User).filter(User.id == row['user_id']).first()
                if not user:
                    continue  # Skip this row if user doesn't exist
                
                application = Application(
                    application_date=app_date,
                    user_id=row['user_id'],
                    target_product=row['target_product'],
                    status=row['status']
                )
                
                db.add(application)
                imported_count += 1
            except Exception as e:
                print(f"Error processing row: {row}, Error: {str(e)}")
                continue
        
        db.commit()
        
        return {"imported_count": imported_count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing applications: {str(e)}")

@router.get("/applications/import-template")
async def get_import_template():
    """
    Generate and return a template Excel file for batch importing applications
    """
    df = pd.DataFrame({
        'application_date': ['2025-04-25'],
        'user_id': [1],
        'target_product': ['C'],
        'status': ['申请中']
    })
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=application_import_template.xlsx"}
    )
