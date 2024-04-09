from pydantic import BaseModel

class RegistrarUsuario(BaseModel):
    usuario: str = None
    password: str = None
    tipo: str = None
    cargo: str = None
    area: str = None
    correo: str = None


class RegistrarReporte(BaseModel):
    nom_reporte: str = None
    descripcion: str = None
    evidencia_1: str = None
    evidencia_2: str = None
    evidencia_3: str = None
    autor: int = None
    estatus: str = None
    urgencia: int = None
    privacidad: int = None
    tipo_reporte: str = None
    responsable: int = None


class EvidenciasAtendido(BaseModel):
    evidencia_1: str = None
    evidencia_2: str = None
    evidencia_3: str = None