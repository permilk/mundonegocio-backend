"""
Sistema de Autenticación JWT con refresh tokens
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
from typing import Optional
import structlog

from config.settings import get_settings

settings = get_settings()
logger = structlog.get_logger()

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos inline
class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool = True
    
class UserInDB(User):
    hashed_password: str
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Modelos
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Funciones de utilidad
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crear refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)  # 30 días
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique identifier
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decodificar y validar token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning("token_decode_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency para obtener usuario actual desde JWT"""
    token = credentials.credentials
    payload = decode_token(token)
    
    # Verificar que sea access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token type inválido",
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    
    # Aquí deberías buscar el usuario en la BD
    # Por ahora retornamos un usuario mock
    user = User(
        id=payload.get("user_id"),
        email=email,
        full_name=payload.get("name"),
        role=UserRole(payload.get("role", "user")),
        country=payload.get("country"),
        is_active=True
    )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verificar que el usuario esté activo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

async def require_role(required_role: UserRole):
    """Dependency para verificar rol"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta operación"
            )
        return current_user
    return role_checker

# Endpoints
@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Autenticar usuario y retornar tokens JWT
    
    **Credenciales de prueba:**
    - Email: admin@mundonegocio.com / Password: admin123
    - Email: vendedor@mundonegocio.com / Password: vendedor123
    """
    # TODO: Buscar usuario en base de datos
    # Por ahora, usuarios hardcodeados para demo
    users_db = {
        "admin@mundonegocio.com": {
            "id": "1",
            "email": "admin@mundonegocio.com",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Administrador Sistema",
            "role": "admin",
            "country": "peru",
            "is_active": True
        },
        "vendedor@mundonegocio.com": {
            "id": "2",
            "email": "vendedor@mundonegocio.com",
            "hashed_password": get_password_hash("vendedor123"),
            "full_name": "Vendedor Demo",
            "role": "user",
            "country": "peru",
            "is_active": True
        }
    }
    
    user_dict = users_db.get(login_data.email)
    
    if not user_dict or not verify_password(login_data.password, user_dict["hashed_password"]):
        logger.warning("login_failed", email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    if not user_dict["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear tokens
    token_data = {
        "sub": user_dict["email"],
        "user_id": user_dict["id"],
        "name": user_dict["full_name"],
        "role": user_dict["role"],
        "country": user_dict["country"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user_dict["email"]})
    
    logger.info("login_success", user_id=user_dict["id"], email=user_dict["email"])
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=User(**{k: v for k, v in user_dict.items() if k != "hashed_password"})
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Renovar access token usando refresh token"""
    payload = decode_token(refresh_data.refresh_token)
    
    # Verificar que sea refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token type inválido",
        )
    
    email = payload.get("sub")
    
    # TODO: Buscar usuario en BD y verificar que el refresh token no haya sido revocado
    
    # Crear nuevo access token
    token_data = {
        "sub": email,
        # Aquí deberías agregar más data del usuario desde la BD
    }
    
    access_token = create_access_token(token_data)
    
    logger.info("token_refreshed", email=email)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,  # Mantener el mismo refresh token
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Cerrar sesión (logout)
    TODO: Agregar refresh token a blacklist en Redis
    """
    logger.info("logout", user_id=current_user.id, email=current_user.email)
    
    return {"message": "Sesión cerrada exitosamente"}

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Cambiar contraseña del usuario"""
    # TODO: Implementar cambio de contraseña en BD
    
    logger.info("password_changed", user_id=current_user.id)
    
    return {"message": "Contraseña cambiada exitosamente"}
