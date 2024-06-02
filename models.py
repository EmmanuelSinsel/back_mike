from pydantic import BaseModel


class RegistrarUsuario(BaseModel):
    matricula: str = None
    usuario: str = None
    password: str = None
    tipo: str = None
    cargo: str = None
    area: str = None
    correo: str = None
    clave_escuela: str = None


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


class RegistrarCategoria(BaseModel):
    nombre_categoria: str = None


class RegistrarArea(BaseModel):
    nombre_area: str = None


class EvidenciasAtendido(BaseModel):
    evidencia_1: str = None
    evidencia_2: str = None
    evidencia_3: str = None


class RegistrarEscuela(BaseModel):
    school_name: str = None
    school_key: str = None
