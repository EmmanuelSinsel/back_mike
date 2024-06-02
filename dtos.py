import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, func, LargeBinary
from sqlalchemy import String, INT, Date, BLOB ,DateTime
from typing import Optional, Annotated
from typing import List

timestamp = Annotated[ #NO SUPE DONDE PONERLO
    datetime.datetime,
    mapped_column(nullable=False),
]
def _get_date():
    return datetime.datetime.now()


class Base(DeclarativeBase):
    pass


class SchoolDatabases(Base):
    __tablename__ = "school_databases"

    id_school: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    school_name: Mapped[str] = mapped_column(String(100), nullable=False)
    database_name: Mapped[str] = mapped_column(String(100), nullable=False)
    school_key: Mapped[str] = mapped_column(String(45), nullable=False)

class Reportes(Base):
    __tablename__ = "reportes"

    ID_report: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    nomReport: Mapped[str] = mapped_column(String(45), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    fecha_report = Column(Date)
    evidencia = Column(LargeBinary)
    autor: Mapped[int] = mapped_column(nullable=False)
    estatus: Mapped[str] = mapped_column(String(30), nullable=False)
    urgencia: Mapped[int] = mapped_column(nullable=False)
    privacidad: Mapped[int] = mapped_column(nullable=False)
    tipo_report: Mapped[str] = mapped_column(String(30), nullable=False)
    responsable: Mapped[int] = mapped_column(nullable=False)
    evidencia_atendido = Column(LargeBinary)

class Usuario(Base):
    __tablename__ = "usuarios"

    ID_user: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    tipoUser: Mapped[str] = mapped_column(String(45), nullable=False)
    nomUser: Mapped[str] = mapped_column(String(100), nullable=False)
    noCuenta: Mapped[str] = mapped_column(String(30), nullable=False)
    passwd: Mapped[str] = mapped_column(String(30), nullable=False)
    cargo: Mapped[str] = mapped_column(String(30), nullable=False)
    area: Mapped[str] = mapped_column(String(300), nullable=False)
    correo: Mapped[str] = mapped_column(String(100), nullable=False)
    estatus: Mapped[int] = mapped_column(nullable=False)


class UsuarioMain(Base):
    __tablename__ = "usuarios_main"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    no_cuenta: Mapped[str] = mapped_column(String(100), nullable=False)
    id_school: Mapped[int] = mapped_column(nullable=False)

class Tokens(Base):
    __tablename__ = "tokens"

    id_tokens: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(nullable=False)
    token: Mapped[str] = mapped_column(String(45), nullable=False)
    token_type: Mapped[str] = mapped_column(String(3), nullable=False)
    expiration = Column(Date)
    expirated: Mapped[int] = mapped_column(nullable=False)


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    nombre_categoria: Mapped[str] = mapped_column(String(500), nullable=False)


class Area(Base):
    __tablename__ = "areas"

    id_area: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    nombre_area: Mapped[str] = mapped_column(String(500), nullable=False)


