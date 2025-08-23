from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List
import uuid
from datetime import datetime, timezone
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions for MongoDB serialization
def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class UserRegistration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=50)
    celular: str = Field(..., min_length=10, max_length=15)
    nombre_negocio: str = Field(..., min_length=1, max_length=100)
    departamento: str = Field(..., min_length=1)
    municipio: str = Field(..., min_length=1, max_length=100)
    numero_celular_negocio: str = Field(..., min_length=10, max_length=15)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator('celular', 'numero_celular_negocio')
    def validate_phone_number(cls, v):
        # Remove any spaces or special characters
        phone = re.sub(r'[^\d]', '', v)
        
        # Check if it's a valid Guatemala phone number (502 + 8 digits)
        if not re.match(r'^502\d{8}$', phone):
            raise ValueError('Número de teléfono debe tener formato internacional válido (ejemplo: 50255556666)')
        
        return phone

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username solo puede contener letras, números y guiones bajos')
        return v

class UserRegistrationCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=50)
    celular: str = Field(..., min_length=10, max_length=15)
    nombre_negocio: str = Field(..., min_length=1, max_length=100)
    departamento: str = Field(..., min_length=1)
    municipio: str = Field(..., min_length=1, max_length=100)
    numero_celular_negocio: str = Field(..., min_length=10, max_length=15)

    @validator('celular', 'numero_celular_negocio')
    def validate_phone_number(cls, v):
        # Remove any spaces or special characters
        phone = re.sub(r'[^\d]', '', v)
        
        # Check if it's a valid Guatemala phone number (502 + 8 digits)
        if not re.match(r'^502\d{8}$', phone):
            raise ValueError('Número de teléfono debe tener formato internacional válido (ejemplo: 50255556666)')
        
        return phone

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username solo puede contener letras, números y guiones bajos')
        return v

# Guatemala departments for validation
GUATEMALA_DEPARTMENTS = [
    "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula", "El Progreso",
    "Escuintla", "Guatemala", "Huehuetenango", "Izabal", "Jalapa", "Jutiapa",
    "Petén", "Quetzaltenango", "Quiché", "Retalhuleu", "Sacatepéquez",
    "San Marcos", "Santa Rosa", "Sololá", "Suchitepéquez", "Totonicapán", "Zacapa"
]

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.get("/departments")
async def get_departments():
    """Get list of Guatemala departments"""
    return {"departments": GUATEMALA_DEPARTMENTS}

@api_router.post("/register")
async def register_user(user_data: UserRegistrationCreate):
    """Register a new user for WABI platform"""
    try:
        # Validate department exists
        if user_data.departamento not in GUATEMALA_DEPARTMENTS:
            raise HTTPException(
                status_code=400, 
                detail=f"Departamento debe ser uno de: {', '.join(GUATEMALA_DEPARTMENTS)}"
            )
        
        # Check if username already exists
        existing_user = await db.user_registrations.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Este nombre de usuario ya está en uso"
            )
        
        # Check if personal phone number already exists
        existing_phone = await db.user_registrations.find_one({"celular": user_data.celular})
        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="Este número de celular ya está registrado"
            )
        
        # Create user registration object
        user_reg = UserRegistration(**user_data.dict())
        user_dict = prepare_for_mongo(user_reg.dict())
        
        # Insert into database
        result = await db.user_registrations.insert_one(user_dict)
        
        if result.inserted_id:
            return {
                "success": True,
                "message": "¡Bienvenido a WABI! Tu negocio ya está en movimiento 🚀",
                "user_id": user_reg.id
            }
        else:
            raise HTTPException(status_code=500, detail="Error al registrar usuario")
            
    except HTTPException:
        # Re-raise HTTPExceptions as they are
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    status_dict = prepare_for_mongo(status_obj.dict())
    _ = await db.status_checks.insert_one(status_dict)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()