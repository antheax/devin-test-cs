from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
import os
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ApplicationStatus(str, enum.Enum):
    PENDING = "申请中"
    COMPLETED = "已完成"

class UserType(str, enum.Enum):
    SUPERADMIN = "超级管理员"
    PROJECT_ADMIN = "项目管理员"
    REGULAR = "普通用户"

class TargetProduct(str, enum.Enum):
    C = "C"
    W = "W"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    tenant = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    project = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    user_type = Column(String(20), default=UserType.REGULAR)
    tabs_accepted = Column(Integer, default=0)
    premium_requests_used = Column(Integer, default=0)
    
    applications = relationship("Application", back_populates="user")

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    update_cycle = Column(Integer, default=30)  # Default to monthly (30 days)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_date = Column(Date, default=datetime.now().date)
    target_product = Column(String(1), nullable=False)
    status = Column(String(20), default=ApplicationStatus.PENDING)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="applications")

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = SessionLocal()
    
    if db.query(Tenant).first() is None:
        tenant1 = Tenant(
            name="租户A",
            update_cycle=30  # Monthly
        )
        
        tenant2 = Tenant(
            name="租户B",
            update_cycle=15  # Bi-weekly
        )
        
        db.add(tenant1)
        db.add(tenant2)
        db.commit()
    
    if db.query(User).first() is None:
        superadmin = User(
            name="管理员",
            email="admin@example.com",
            tenant="租户A",
            department="管理部",
            project="系统管理",
            role="系统管理员",
            user_type=UserType.SUPERADMIN,
            tabs_accepted=0,
            premium_requests_used=0
        )
        
        project_admin = User(
            name="项目管理",
            email="project@example.com",
            tenant="租户A",
            department="研发部",
            project="项目1",
            role="项目管理员",
            user_type=UserType.PROJECT_ADMIN,
            tabs_accepted=5,
            premium_requests_used=2
        )
        
        user1 = User(
            name="张三",
            email="zhangsan@example.com",
            tenant="租户A",
            department="研发部",
            project="项目1",
            role="开发工程师",
            user_type=UserType.REGULAR,
            tabs_accepted=10,
            premium_requests_used=5
        )
        
        user2 = User(
            name="李四",
            email="lisi@example.com",
            tenant="租户B",
            department="产品部",
            project="项目2",
            role="产品经理",
            user_type=UserType.REGULAR,
            tabs_accepted=8,
            premium_requests_used=3
        )
        
        db.add(superadmin)
        db.add(project_admin)
        db.add(user1)
        db.add(user2)
        db.commit()
        
        app1 = Application(
            application_date=datetime.now().date(),
            target_product=TargetProduct.C,
            status=ApplicationStatus.COMPLETED,
            user_id=3  # user1 (张三)
        )
        
        app2 = Application(
            application_date=datetime.now().date(),
            target_product=TargetProduct.W,
            status=ApplicationStatus.PENDING,
            user_id=4  # user2 (李四)
        )
        
        db.add(app1)
        db.add(app2)
        db.commit()
    
    db.close()
