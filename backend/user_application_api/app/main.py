from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables, init_db
from app.routers import users, applications, tenants

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(users.router)
app.include_router(applications.router)
app.include_router(tenants.router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    create_tables()
    init_db()
