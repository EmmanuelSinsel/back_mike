from database import Database
from sqlalchemy import select, or_

from models import *

from dtos import *


class Repo:
    db = None

    def __init__(self):
        db_obj = Database()
        self.db = db_obj.connection()

    def login(self, usuario: str, password: str):
        try:
            user = self.db.query(Usuario).filter(Usuario.nomUser == usuario).order_by(Usuario.ID_user).first()
            if user.passwd == password:
                return True, {"status": 1, "detail": "sesion iniciada"}
            else:
                return False, {"status": 0, "detail": "contraseña incorrecta"}
        except Exception as err:
            print(err)
            return False, {"detail": err}

    def registrar(self, data: RegistrarUsuario):
        user = Usuario(
            tipoUser=data.tipo,
            nomUser=data.usuario,
            passwd=data.password,
            cargo=data.cargo,
            area=data.area
        )
        try:
            self.db.add(user)
            self.db.commit()
            return True, {"detail", "Succesful Insert"}
        except Exception as err:
            print(err)
            return False, {"detail": err}

    def generar_reporte(self, data: RegistrarReporte):
        pass

    def ver_historial(self, id_usuario: int):
        pass

    def eliminar_reporte(self, id_reporte: int):
        pass

    def repostear_reporte(self, id_reporte: int):
        pass

    def ver_reportes(self, id_usuario: int):
        pass

    def ver_detalles(self, id_reporte: int):
        pass

    def actualizar_estado(self, id_reporte: int, estado: str):
        pass

    def reasignar(self, id_reporte: int, id_usuario: int):
        pass
