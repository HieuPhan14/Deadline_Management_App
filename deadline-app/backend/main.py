from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from contextlib import asynccontextmanager
from routers.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup - run when app starts
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown - runs when app stops

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

@app.get("/")
async def root():
    return {"message": "Deadline Management App API"}
