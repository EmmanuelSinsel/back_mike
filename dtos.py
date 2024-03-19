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

class Reportes(Base):
    __tablename__ = "reportes"

    ID_report: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    nomReport: Mapped[str] = mapped_column(String(45), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(45), nullable=False)
    fecha_report = Column(Date)
    evidencia = Column(LargeBinary)
    autor: Mapped[int] = mapped_column(nullable=False)
    estatus: Mapped[str] = mapped_column(String(30), nullable=False)
    urgencia: Mapped[int] = mapped_column(nullable=False)
    privacidad: Mapped[int] = mapped_column(nullable=False)
    tipo_report: Mapped[str] = mapped_column(String(30), nullable=False)
    responsable: Mapped[int] = mapped_column(nullable=True)
    evidencia_atendido = Column(LargeBinary)

class Usuario(Base):
    __tablename__ = "usuarios"

    ID_user: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    tipoUser: Mapped[str] = mapped_column(String(45), nullable=False)
    nomUser: Mapped[str] = mapped_column(String(45), nullable=False)
    passwd: Mapped[str] = mapped_column(String(30), nullable=False)
    cargo: Mapped[str] = mapped_column(String(30), nullable=False)
    area: Mapped[str] = mapped_column(String(30), nullable=False)