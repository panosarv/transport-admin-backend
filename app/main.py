from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import bookings
from app.routers import vehicles
from app.routers import articles
from app.routers import users 
app = FastAPI(title="Transport Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(vehicles.router)
app.include_router(articles.router)
app.include_router(users.router)
