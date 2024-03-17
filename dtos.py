from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String, INT, Date, BLOB
from typing import Optional
from typing import List

class Base(DeclarativeBase):
    pass

class Reportes(Base):
    __tablename__ = "reportes"

    ID_report: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    nomReport: Mapped[str] = mapped_column(String(45), nullable=False)
    decripcion: Mapped[str] = mapped_column(String(45), nullable=False)
    evidencia = mapped_column(BLOB, nullable=False)
    autor: Mapped[int] = mapped_column(nullable=False)
    estatus: Mapped[str] = mapped_column(String(30), nullable=False)
    urgencia: Mapped[int] = mapped_column(nullable=False)
    privacidad: Mapped[int] = mapped_column(nullable=False)
    tipo_report: Mapped[str] = mapped_column(String(30), nullable=False)
    responsabble: Mapped[int] = mapped_column(nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    ID_user: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    tipoUser: Mapped[str] = mapped_column(String(45), nullable=False)
    nomUser: Mapped[str] = mapped_column(String(45), nullable=False)
    passwd: Mapped[str] = mapped_column(String(30), nullable=False)
    cargo: Mapped[str] = mapped_column(String(30), nullable=False)
    area: Mapped[str] = mapped_column(String(30), nullable=False)