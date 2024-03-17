from pydantic import BaseModel

class RegistrarUsuario(BaseModel):
    usuario: str = None
    password: str = None
    tipo: str = None
    cargo: str = None
    area: str = None

class RegistrarReporte(BaseModel):
    id_reporte: int = None
    nom_reporte: str = None
    descripcion: str = None
    fecha_reporte: str = None
    evidencia: str = None
    autor: int = None
    estatus: str = None
    urgencia: int = None
    privacidad: int = None
    tipo_reporte: str = None