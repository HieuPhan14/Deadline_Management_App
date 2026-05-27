from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from contextlib import asynccontextmanager
from routers.auth import router as auth_router
from models.user import User
from routers.deps import get_current_user
from routers.import_ import router as import_router
from routers.dashboard import router as dashboard_router
from routers.tasks import router as tasks_router
from services.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup - run when app starts
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    # shutdown - runs when app stops
    stop_scheduler()

app = FastAPI(
    title="Deadline Management App",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - allows React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(import_router)
app.include_router(dashboard_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Deadline Management App API"}

@app.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }

