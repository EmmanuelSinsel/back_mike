import base64
import json

import sqlalchemy

from database import Database
from sqlalchemy import select, or_
import datetime
from datetime import date
from models import *

from dtos import *

import smtplib
from email.mime.text import MIMEText
import string
from datetime import date, timedelta, datetime
from dateutil.parser import parse

import random


class Repo:
    db = None
    characters = string.ascii_letters + string.digits
    dominio = "reportesuasfim.ddns.net"

    def __init__(self):
        db_obj = Database()
        self.db = db_obj.connection()
    def login(self, no_cuenta: str, password: str):
        try:
            user = self.db.query(Usuario).filter(Usuario.noCuenta == no_cuenta).order_by(Usuario.ID_user).first()
            if user:
                if user.passwd == password:
                    return True, {"status": 1, "detail": "sesion iniciada","usuario":user}
                else:
                    return False, {"status": 0, "detail": "contraseña incorrecta"}
            else:
                return False, {"status": 0, "detail": "usuario inexistente"}
        except Exception as err:
            print(err)
            return False, {"detail": err}

    def registrar(self, data: RegistrarUsuario):
        user = Usuario(
            tipoUser=data.tipo,
            nomUser=data.usuario,
            noCuenta=data.matricula, #
            passwd=data.password, #
            cargo=data.cargo,
            area=data.area,
            correo=data.correo #
        )
        try:
            get_user = self.db.query(Usuario).filter(Usuario.noCuenta == data.matricula).order_by(Usuario.ID_user).first()
            if not get_user:
                self.db.add(user)
                self.db.flush()
                self.db.commit()
                self.db.refresh(user)
                self.sendEmailVerification(id_usuario=user.ID_user, email=user.correo)
                return True, {"status": 1, "detail": "Succesful Insert"}
            else:
                return False, {"status": 0, "detail": "Usuario ya Existe"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def registrar_usuario(self, data: RegistrarUsuario):
            user = Usuario(
                tipoUser=data.tipo,
                nomUser=data.usuario,
                noCuenta=data.matricula,  #
                passwd=data.password,  #
                cargo=data.cargo,
                area=data.area,
                correo=data.correo  #
            )
            try:
                get_user = self.db.query(Usuario).filter(Usuario.noCuenta == data.matricula).order_by(
                    Usuario.ID_user).first()
                if not get_user:
                    self.db.add(user)
                    self.db.flush()
                    self.db.commit()
                    self.db.refresh(user)
                    self.sendEmailVerification(id_usuario=user.ID_user, email=user.correo)
                    return True, {"status": 1, "detail": "Succesful Insert"}
                else:
                    return False, {"status": 0, "detail": "Usuario ya Existe"}
            except Exception as err:
                print(err)
                return False, {"status": 0, "detail": err}

    def reasignar_area(self, id_usuario: int, area: str, tipoUser: str):
        try:
            usuario = self.db.query(Usuario).filter(Usuario.ID_user == id_usuario).first()
            usuario.area = area
            usuario.tipoUser = tipoUser

            if tipoUser == 'Estudiante':
                usuario.area = 'NA'

            if tipoUser == 'Administrador':
                usuario.tipoUser = 'SuperAdmin'
                usuario.area = 'Direccion'

            self.db.commit()
            return True, {"status": 1, "detail": "Datos del usuario actualizadados"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def detalle_usuario(self, id_usuario: int):
        try:
            usuario = self.db.query(Usuario).filter(Usuario.ID_user == id_usuario).first()
            data = {
                "ID_user": usuario.ID_user,
                "tipoUser": usuario.tipoUser,
                "nomUser": usuario.nomUser,
                "noCuenta": usuario.noCuenta,
                "passwd": usuario.passwd,
                "cargo": usuario.cargo,
                "area": usuario.area,
                "correo": usuario.correo,
                "estatus": usuario.estatus,
                "reportes": None
            }
            if usuario.tipoUser == 'Estudiante':
                reportes = self.db.query(Reportes).filter(Reportes.autor == id_usuario).all()
                if reportes:
                    temp = []
                    for i in reportes:
                        temp.append({
                            "ID_report": i.ID_report,
                            "nomReport": i.nomReport,
                            "fecha_report": i.fecha_report,
                            "estatus": i.estatus,
                            "urgencia": i. urgencia
                        })
                    data['reportes'] = temp
            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}
    def generar_reporte(self, data: RegistrarReporte):
        fecha_actual = date.today()
        print(fecha_actual)
        evidencia = {
            "evidencia_1": data.evidencia_1,
            "evidencia_2": data.evidencia_2,
            "evidencia_3": data.evidencia_3,
        }
        evidencia_bytes = json.dumps(evidencia).encode(encoding="UTF-8")
        #print(evidencia)
        reporte = Reportes(
            nomReport=data.nom_reporte,
            descripcion=data.descripcion,
            evidencia=base64.b64encode(evidencia_bytes),
            fecha_report=date(fecha_actual.year, fecha_actual.month, fecha_actual.day),
            autor=data.autor,
            estatus=data.estatus,
            urgencia=data.urgencia,
            privacidad=data.privacidad,
            tipo_report=data.tipo_reporte,
            responsable=data.responsable
        )
        try:
            self.db.add(reporte)
            self.db.commit()
            return True, {"status": 1, "detail": "Succesful Insert"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def ver_historial(self,
                      id_usuario: int,
                      estatus: str = None,
                      tipo_report: str = None,
                      urgencia: bool = False):
        query_full = None
        query_estatus = None
        query_tipo = None
        try:
            if urgencia:
                if estatus == None and tipo_report == None:
                    query_full = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                  .order_by(Reportes.urgencia.desc()).all())
                else:
                    if type(estatus) == str and type(tipo_report) == str:
                        query_full = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                      .filter(Reportes.tipo_report == tipo_report)
                                      .filter(Reportes.estatus == estatus).order_by(
                            Reportes.urgencia.desc()).all())
                    else:
                        if type(estatus) == str:
                            query_estatus = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                             .filter(Reportes.estatus == estatus).order_by(
                                Reportes.urgencia.desc()).all())
                        if type(tipo_report) == str:
                            query_tipo = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                          .filter(Reportes.tipo_report == tipo_report).order_by(
                                Reportes.urgencia.desc()).all())
            else:
                if type(estatus) == str and type(tipo_report) == str:
                    query_full = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                  .filter(Reportes.tipo_report == tipo_report)
                                  .filter(Reportes.estatus == estatus).all())
                else:
                    if type(estatus) == str:
                        query_estatus = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                         .filter(Reportes.estatus == estatus).all())
                    if type(tipo_report) == str:
                        query_tipo = (self.db.query(Reportes).filter(Reportes.autor == id_usuario)
                                      .filter(Reportes.tipo_report == tipo_report).all())
            if query_full == None:
                if query_estatus:
                    query_full = query_estatus
                if query_tipo:
                    query_full = query_tipo
            data = {}
            cont = 1
            if query_full:
                for i in query_full:
                    autor = self.db.query(Usuario).filter(Usuario.ID_user == i.autor).order_by(Usuario.ID_user).first()
                    row = {
                        "ID_report": i.ID_report,
                        "nomReport": i.nomReport,
                        "fecha_report": i.fecha_report,
                        "estatus": i.estatus,
                        "autor": {
                            "ID_user": autor.ID_user,
                            "nomUser": autor.nomUser,
                            "noCuenta": autor.noCuenta
                        },
                        "tipo_report": i.tipo_report,
                        "urgencia": i.urgencia
                    }
                    data[cont] = row
                    cont += 1
                return True, data
            else:
                return True, {}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def ver_historial_responsable(self,
                      id_responsable: int,
                      estatus: str = None,
                      tipo_report: str = None,
                      urgencia: bool = False):
        query_full = None
        query_estatus = None
        query_tipo = None
        try:
            if urgencia:
                if estatus == None and tipo_report == None:
                    query_full = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                  .order_by(Reportes.urgencia.desc()).all())
                else:
                    if type(estatus) == str and type(tipo_report) == str:
                        query_full = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                      .filter(Reportes.tipo_report == tipo_report)
                                      .filter(Reportes.estatus == estatus).order_by(
                            Reportes.urgencia.desc()).all())
                    else:
                        if type(estatus) == str:
                            query_estatus = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                             .filter(Reportes.estatus == estatus).order_by(
                                Reportes.urgencia.desc()).all())
                        if type(tipo_report) == str:
                            query_tipo = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                          .filter(Reportes.tipo_report == tipo_report).order_by(
                                Reportes.urgencia.desc()).all())
            else:
                if type(estatus) == str and type(tipo_report) == str:
                    query_full = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                  .filter(Reportes.tipo_report == tipo_report)
                                  .filter(Reportes.estatus == estatus).all())
                else:
                    if type(estatus) == str:
                        query_estatus = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                         .filter(Reportes.estatus == estatus).all())
                    if type(tipo_report) == str:
                        query_tipo = (self.db.query(Reportes).filter(Reportes.responsable == id_responsable)
                                      .filter(Reportes.tipo_report == tipo_report).all())
            if query_full == None:
                if query_estatus:
                    query_full = query_estatus
                if query_tipo:
                    query_full = query_tipo
            data = {}
            cont = 1
            if query_full:
                for i in query_full:
                    autor = self.db.query(Usuario).filter(Usuario.ID_user == i.autor).order_by(Usuario.ID_user).first()
                    row = {
                        "ID_report": i.ID_report,
                        "nomReport": i.nomReport,
                        "fecha_report": i.fecha_report,
                        "estatus": i.estatus,
                        "autor": {
                            "ID_user": autor.ID_user,
                            "nomUser": autor.nomUser,
                            "noCuenta": autor.noCuenta
                        },
                        "tipo_report": i.tipo_report,
                        "urgencia": i.urgencia
                    }
                    data[cont] = row
                    cont += 1
                return True, data
            else:
                return True, {}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def eliminar_reporte(self, id_reporte: int):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
            if reporte:
                self.db.delete(reporte)
                self.db.commit()
                return True, {"status": 1, "detail": "Succesful Delete"}
            else:
                return True, {"status": 0, "detail": "Reporte not found"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def repostear_reporte(self, id_reporte: int):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
            if reporte:
                reporte.urgencia += 1
                self.db.commit()
                return True, {"status": 1, "detail": "Succesful Update"}
            else:
                return True, {"status": 0, "detail": "Reporte not found"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def ver_reportes(self,
                     estatus: str = 'Pendiente',
                     tipo_report=None,
                     urgencia=False,
                     sin_asignar=False):
        query_full = None
        query_estatus = None
        query_tipo = None
        try:
            query_full = self.db.query(Reportes)
            if urgencia:
                query_full = query_full.order_by(Reportes.urgencia.desc())
            else:
                query_full = query_full.order_by(Reportes.fecha_report.desc())
            if estatus is not None:
                query_full = query_full.filter(or_(Reportes.estatus == estatus, Reportes.estatus == 'Asignado'))
            if tipo_report is not None:
                query_full = query_full.filter(Reportes.tipo_report == tipo_report)
            if sin_asignar:
                query_full = query_full.filter(Reportes.responsable == 0)
            query_full = query_full.all()
            # if urgencia:
            #     if estatus == None and tipo_report == None:
            #         query_full = (self.db.query(Reportes)
            #                       .order_by(Reportes.urgencia.desc()).all())
            #     else:
            #         if type(estatus) == str and type(tipo_report) == str:
            #             query_full = (self.db.query(Reportes)
            #                           .filter(Reportes.tipo_report == tipo_report)
            #                           .filter(Reportes.estatus == estatus).order_by(
            #                 Reportes.urgencia.desc()).all())
            #         else:
            #             if type(estatus) == str:
            #                 query_estatus = (self.db.query(Reportes)
            #                                  .filter(Reportes.estatus == estatus)
            #                                  .order_by(Reportes.urgencia.desc()).all())
            #             if type(tipo_report) == str:
            #                 query_tipo = (self.db.query(Reportes)
            #                               .filter(Reportes.tipo_report == tipo_report).order_by(
            #                     Reportes.urgencia.desc()).all())
            #
            # else:
            #     if estatus == None and tipo_report == None:
            #         query_full = (self.db.query(Reportes)
            #                       .order_by(Reportes.fecha_report.desc()).all())
            #     else:
            #         if type(estatus) == str and type(tipo_report) == str:
            #             query_full = (self.db.query(Reportes)
            #                           .filter(Reportes.tipo_report == tipo_report)
            #                           .filter(Reportes.estatus == estatus and Reportes.responsable == 0).order_by(
            #                 Reportes.fecha_report.desc()).all())
            #         else:
            #             if type(estatus) == str:
            #                 query_estatus = (self.db.query(Reportes)
            #                                  .filter(Reportes.estatus == estatus and Reportes.responsable == 0).order_by(
            #                     Reportes.fecha_report.desc()).all())
            #             if type(tipo_report) == str:
            #                 query_tipo = (self.db.query(Reportes)
            #                               .filter(Reportes.tipo_report == tipo_report).order_by(
            #                     Reportes.fecha_report.desc()).all())
            # if query_full == None:
            #     if query_estatus:
            #         query_full = query_estatus
            #     if query_tipo:
            #         query_full = query_tipo
            data = {}
            cont = 1
            if query_full:
                for i in query_full:
                    autor = self.db.query(Usuario).filter(Usuario.ID_user == i.autor).order_by(Usuario.ID_user).first()
                    row = {
                        "ID_report": i.ID_report,
                        "nomReport": i.nomReport,
                        "fecha_report": i.fecha_report,
                        "estatus": i.estatus,
                        "autor": {
                            "ID_user": autor.ID_user,
                            "nomUser": autor.nomUser,
                            "noCuenta": autor.noCuenta
                        },
                        "tipo_report": i.tipo_report,
                        "urgencia": i.urgencia
                    }
                    data[cont] = row
                    cont += 1
                return True, data
            else:
                return True, {}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def ver_detalles(self, id_reporte: int):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).order_by(
                Reportes.ID_report).first()
            autor = self.db.query(Usuario).filter(Usuario.ID_user == reporte.autor).order_by(Usuario.ID_user).first()

            responsable = self.db.query(Usuario).filter(Usuario.ID_user == reporte.responsable).order_by(
                Usuario.ID_user).first() if reporte.responsable != 0 else None

            evidencia = json.loads(base64.b64decode(reporte.evidencia).decode("UTF-8"))

            data = {
                "ID_report": reporte.ID_report,
                "nomReporte": reporte.nomReport,
                "descripcion": reporte.descripcion,
                "fecha_report": reporte.fecha_report,
                "evidencia": {
                    "evidencia_1": evidencia.get("evidencia_1", ""),
                    "evidencia_2": evidencia.get("evidencia_2", ""),
                    "evidencia_3": evidencia.get("evidencia_3", ""),
                },
                "evidencia_atendido": {},
                "autor": {
                    "ID_user": autor.ID_user,
                    "nomUser": autor.nomUser,
                },
                "estatus": reporte.estatus,
                "urgencia": reporte.urgencia,
                "tipo_report": reporte.tipo_report,
            }

            if responsable:
                data["responsable"] = {
                    "ID_user": responsable.ID_user,
                    "nomUser": responsable.nomUser,
                    "cargo": responsable.cargo,
                    "area": responsable.area
                }
            else:
                data["responsable"] = None  # O cualquier otro valor que desees usar cuando el responsable sea 0

            if reporte.evidencia_atendido:
                evidencia_atendido = json.loads(base64.b64decode(reporte.evidencia_atendido).decode("UTF-8"))
                data["evidencia_atendido"] = {
                    "evidencia_1": evidencia_atendido.get("evidencia_1", ""),
                    "evidencia_2": evidencia_atendido.get("evidencia_2", ""),
                    "evidencia_3": evidencia_atendido.get("evidencia_3", ""),
                }
            else:
                data["evidencia_atendido"] = "null"

            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": str(err)}

    def actualizar_estado(self,
                          id_reporte: int,
                          estado: str):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
            if reporte:
                reporte.estatus = estado
                self.db.commit()
                return True, {"status": 1, "detail": "Succesful Update"}
            else:
                return True, {"status": 0, "detail": "Reporte not found"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def evidencias_atendido(self,
                            id_reporte: int,
                            data: EvidenciasAtendido):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
            if reporte:
                evidencia = {
                    "evidencia_1": data.evidencia_1,
                    "evidencia_2": data.evidencia_2,
                    "evidencia_3": data.evidencia_3,
                }
                evidencia_bytes = json.dumps(evidencia).encode(encoding="UTF-8")
                reporte.evidencia_atendido = base64.b64encode(evidencia_bytes)
                self.db.commit()
            return True, {"status": 1, "detail": "Succesful Update"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    # def reasignar(self,
    #               id_reporte: int,
    #               area: str):
    #     try:
    #         usuarios = self.db.query(Usuario).filter(Usuario.area == area).all()
    #         reporte_count = []
    #         for i in usuarios:
    #             reportes = (self.db.query(Reportes).filter(Reportes.responsable == i.ID_user)
    #
    #             .filter(Reportes.estatus != "Resuelto").count())
    #             reporte_count.append(reportes)
    #         min = -1
    #         min_id = 0
    #         for i in range(0, len(reporte_count)):
    #             if min == -1 or reporte_count[i] < min:
    #                 min = reporte_count[i]
    #                 min_id = i
    #         reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
    #         if reporte:
    #             reporte.responsable = usuarios[min_id].ID_user
    #             self.db.commit()
    #             return True, {"status": 1, "detail": "Succesful Update"}
    #         else:
    #             return True, {"status": 0, "detail": "Reporte not found"}
    #     except Exception as err:
    #         print(err)
    #         return False, {"status": 0, "detail": err}
    def reasignar(self, id_reporte: int, area: str, ID_user: int):
        try:
            # Obtener todos los usuarios del área específica
            usuarios = self.db.query(Usuario).filter(Usuario.area == area).all()

            # Verificar si existe al menos un usuario en el área
            if usuarios:
                # Reasignar el reporte al usuario con el ID recibido
                reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
                if reporte:
                    reporte.responsable = ID_user
                    reporte.estatus = 'Asignado'
                    self.db.commit()
                    return True, {"status": 1, "detail": "Succesful Update"}
                else:
                    return True, {"status": 0, "detail": "Reporte not found"}
            else:
                return True, {"status": 0, "detail": "No users found in the specified area"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": str(err)}



    #  EMAILS

    def sendEmailVerification(self,
                              id_usuario: int,
                              email: str):
        sender = emailSender(sender="therealchalinosanchez@gmail.com", password="mlta vekc irlj exls")
        code = ""
        while True:
            p1 = ''.join(random.choice(self.characters) for i in range(3))
            p2 = ''.join(random.choice(self.characters) for i in range(3))
            p3 = ''.join(random.choice(self.characters) for i in range(3))
            code = p1 + "-" + p2 + "-" + p3
            print(code)
            get_tokens = self.db.query(Tokens).filter(Tokens.token == code).filter(Tokens.token_type == "reg").count()
            if get_tokens == 0:
                break

        expiration_date = datetime.now() + timedelta(minutes=30)

        token = Tokens(
            id_usuario=id_usuario,
            token=code,
            token_type="reg",
            expiration=expiration_date,
            expirated=False
        )
        self.db.add(token)
        self.db.commit()
        message = ("Bienvenido a la plataforma de reportes de la Facultad de Ingenieria Mochis, para activar tu cuenta "
                   "es necesario activarla con el siguiente codigo: " + code + " o ingresando al siguiente link "
                                                                               "http://" + self.dominio + "/activar?token=" + code)
        sender.sendEmail(subject="VERIFICACION DE CORREO",
                         recipients=email,
                         message=message,
                         code=code)

    def verificarToken(self, token: str):
        try:
            token_data = self.db.query(Tokens).filter(Tokens.token == token).filter(Tokens.token_type == "reg").first()
            expiration_date = parse(str(token_data.expiration))
            today = parse(str(datetime.today()))
            if token_data.expirated == False:
                if today < expiration_date:
                    #print('id del usuario a activar: ' + token_data.id_usuario)
                    usuario = self.db.query(Usuario).filter(Usuario.ID_user == token_data.id_usuario).first()
                    token_data.expirated = True
                    usuario.estatus = 1
                    self.db.commit()
                    return True, {"status": 1, "detail": "Activado"}
                else:
                    return True, {"status": 0, "detail": "Codigo vencido"}
            else:
                return True, {"status": 2, "detail": "Codigo ya activado"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def enviarCorreoPasswordReset(self,
                                  email: str,
                                  id_usuario: int):
        sender = emailSender(sender="therealchalinosanchez@gmail.com", password="mlta vekc irlj exls")
        code = ""
        while True:
            p1 = ''.join(random.choice(self.characters) for i in range(3))
            p2 = ''.join(random.choice(self.characters) for i in range(3))
            p3 = ''.join(random.choice(self.characters) for i in range(3))
            code = p1 + "-" + p2 + "-" + p3
            print(code)
            get_tokens = self.db.query(Tokens).filter(Tokens.token == code).filter(Tokens.token_type == "pwr").count()
            if get_tokens == 0:
                break

        expiration_date = datetime.now() + timedelta(minutes=30)

        token = Tokens(
            id_usuario=id_usuario,
            token=code,
            token_type="pwr",
            expiration=expiration_date,
            expirated=False
        )
        try:
            self.db.add(token)
            self.db.commit()
            message = ("Para reestablecer tu contraseña debes introducir el siguiente codigo: " + code +
                       " o ingresando al siguiente link http://" + self.dominio + "/recuperacion?token=" + code)
            sender.sendEmail(subject="RECUPERACION DE CONTRASEÑA",
                             recipients=email,
                             message=message,
                             code=code)
            return True, {"status": 1, "detail": "Codigo enviado"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def passwordReset(self,
                      token: str,
                      new_password: str):
        try:
            token_data = self.db.query(Tokens).filter(Tokens.token == token).filter(
                Tokens.token_type == "[pwr]").first()
            expiration_date = parse(str(token_data.expiration))
            today = parse(str(datetime.today()))
            if token_data.expirated == False:
                if today < expiration_date:
                    token_data.expirated = True
                    user_data = self.db.query(Usuario).filter(Usuario.ID_user == token_data.id_usuario).first()
                    user_data.passwd = new_password
                    self.db.commit()
                    return True, {"status": 1, "detail": "Activado"}
                else:
                    return True, {"status": 0, "detail": "Codigo vencido"}
            else:
                return True, {"status": 2, "detail": "Codigo ya activado"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def lista_usuarios(self):
        try:
            usuarios = self.db.query(Usuario).filter(Usuario.tipoUser != 'SuperAdmin').all()
            data = []
            for i in usuarios:
                data.append({
                    "ID_user": i.ID_user,
                    "tipoUser": i.tipoUser,
                    "nomUser": i.nomUser,
                    "noCuenta": i.noCuenta,
                    "passwd": i.passwd,
                    "cargo": i.cargo,
                    "area": i.area,
                    "correo": i.correo,
                    "estatus": i.estatus,
                })
            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def lista_usuarios_area(self, area: str):
        try:
            usuarios = self.db.query(Usuario).filter(Usuario.area == area).all()
            data = []
            for i in usuarios:
                data.append({
                    "ID_user": i.ID_user,
                    "tipoUser": i.tipoUser,
                    "nomUser": i.nomUser,
                    "noCuenta": i.noCuenta,
                    "passwd": i.passwd,
                    "cargo": i.cargo,
                    "area": i.area,
                    "correo": i.correo,
                    "estatus": i.estatus,
                })
            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def lista_categorias(self):
        try:
            cat = self.db.query(Categoria).all()
            data = []
            for i in cat:
                data.append({
                    "id_categoria": i.id_categoria,
                    "nombre_categoria": i.nombre_categoria
                })
            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def registrar_categoria(self,
                            categoria: RegistrarCategoria):
        try:
            cat = Categoria(
                nombre_categoria=categoria.nombre_categoria
            )
            self.db.add(cat)
            self.db.commit()
            return True, {"status": 1, "detail": "Categoria Registrada"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def eliminar_categoria(self,
                           id_categoria: int):
        try:
            cat = self.db.query(Categoria).filter(Categoria.id_categoria == id_categoria).first()
            self.db.delete(cat)
            self.db.commit()
            return True, {"status": 1, "detail": "Categoria Eliminada"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def actualizar_categoria(self,
                             id_categoria,
                             categoria: RegistrarCategoria):
        try:
            cat = self.db.query(Categoria).where(Categoria.id_categoria == id_categoria).first()
            cat.nombre_categoria = categoria.nombre_categoria
            self.db.commit()
            return True, {"status": 1, "detail": "Categoria Actualizada"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    #AREAS

    def lista_areas(self):
        try:
            area = self.db.query(Area).all()
            data = []
            for i in area:
                data.append({
                    "id_area": i.id_area,
                    "nombre_area": i.nombre_area
                })
            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def registrar_area(self,
                       area: RegistrarArea):
        try:
            area = Area(
                nombre_area=area.nombre_area
            )
            self.db.add(area)
            self.db.commit()
            return True, {"status": 1, "detail": "Area Registrada"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def eliminar_area(self,
                      id_area: int):
        try:
            area = self.db.query(Area).filter(Area.id_area == id_area).first()
            self.db.delete(area)
            self.db.commit()
            return True, {"status": 1, "detail": "Area Eliminada"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def actualizar_area(self,
                             id_area,
                             area: RegistrarArea):
        try:
            cat = self.db.query(Area).where(Area.id_area == id_area).first()
            cat.nombre_area = area.nombre_area
            self.db.commit()
            return True, {"status": 1, "detail": "Area Actualizada"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}


class emailSender:
    sender = ""
    password = ""

    def __init__(self, sender, password):
        self.sender = sender
        self.password = password

    def sendEmail(self, subject, recipients, message, code):
        msg = MIMEText(message, 'plain')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(recipients)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(self.sender, self.password)
            smtp_server.sendmail(self.sender, recipients, msg.as_string())
        print("Message sent!")




