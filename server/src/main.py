from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.env import vars
from src.router import router

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=[vars.CLIENT_URL],
    allow_credentials=True, 
    allow_methods=['*'],    
    allow_headers=['*'],
)
api.include_router(router)
