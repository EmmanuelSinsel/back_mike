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

    def login(self, usuario: str, password: str):
        try:
            user = self.db.query(Usuario).filter(Usuario.nomUser == usuario).order_by(Usuario.ID_user).first()
            if user:
                if user.passwd == password:
                    return True, {"status": 1, "detail": "sesion iniciada"}
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
            passwd=data.password,
            cargo=data.cargo,
            area=data.area,
            correo=data.correo
        )
        try:
            get_user = self.db.query(Usuario).filter(Usuario.nomUser == data.usuario).order_by(Usuario.ID_user).first()
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

    def generar_reporte(self, data: RegistrarReporte):
        fecha_actual = date.today()
        print(fecha_actual)
        evidencia = {
            "evidencia_1": data.evidencia_1,
            "evidencia_2": data.evidencia_2,
            "evidencia_3": data.evidencia_3,
        }
        evidencia_bytes = json.dumps(evidencia).encode(encoding="UTF-8")
        print(evidencia)
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
                            "nomUser": autor.nomUser
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
                     estatus=None,
                     tipo_report=None,
                     urgencia=False):
        query_full = None
        query_estatus = None
        query_tipo = None
        try:
            if urgencia:
                if estatus == None and tipo_report == None:
                    query_full = (self.db.query(Reportes)
                                  .order_by(Reportes.urgencia.desc()).all())
                else:
                    if type(estatus) == str and type(tipo_report) == str:
                        query_full = (self.db.query(Reportes)
                                      .filter(Reportes.tipo_report == tipo_report)
                                      .filter(Reportes.estatus == estatus).order_by(
                            Reportes.urgencia.desc()).all())
                    else:
                        if type(estatus) == str:
                            query_estatus = (self.db.query(Reportes)
                                             .filter(Reportes.estatus == estatus).order_by(
                                Reportes.urgencia.desc()).all())
                        if type(tipo_report) == str:
                            query_tipo = (self.db.query(Reportes)
                                          .filter(Reportes.tipo_report == tipo_report).order_by(
                                Reportes.urgencia.desc()).all())

            else:
                if estatus == None and tipo_report == None:
                    query_full = (self.db.query(Reportes)
                                  .order_by(Reportes.fecha_report.desc()).all())
                else:
                    if type(estatus) == str and type(tipo_report) == str:
                        query_full = (self.db.query(Reportes)
                                      .filter(Reportes.tipo_report == tipo_report)
                                      .filter(Reportes.estatus == estatus).order_by(
                            Reportes.fecha_report.desc()).all())
                    else:
                        if type(estatus) == str:
                            query_estatus = (self.db.query(Reportes)
                                             .filter(Reportes.estatus == estatus).order_by(
                                Reportes.fecha_report.desc()).all())
                        if type(tipo_report) == str:
                            query_tipo = (self.db.query(Reportes)
                                          .filter(Reportes.tipo_report == tipo_report).order_by(
                                Reportes.fecha_report.desc()).all())
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
                            "nomUser": autor.nomUser
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

    def ver_detalles(self,
                     id_reporte: int):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).order_by(
                Reportes.ID_report).first()
            autor = self.db.query(Usuario).filter(Usuario.ID_user == reporte.autor).order_by(Usuario.ID_user).first()
            responsable = self.db.query(Usuario).filter(Usuario.ID_user == reporte.responsable).order_by(
                Usuario.ID_user).first()
            evidencia = json.loads(base64.b64decode(reporte.evidencia).decode("UTF-8"))
            data = {
                "ID_report": reporte.ID_report,
                "nomReporte": reporte.nomReport,
                "descripcion": reporte.descripcion,
                "fecha_report": reporte.fecha_report,
                "evidencia": {
                    "evidencia_1": evidencia["evidencia_1"],
                    "evidencia_2": evidencia["evidencia_2"],
                    "evidencia_3": evidencia["evidencia_3"],
                },
                "evidencia_atendido": {},
                "autor": {
                    "ID_user": autor.ID_user,
                    "nomUser": autor.nomUser,
                },
                "estatus": reporte.estatus,
                "urgencia": reporte.urgencia,
                "tipo_report": reporte.tipo_report,
                "responsable": {
                    "ID_user": responsable.ID_user,
                    "nomUser": responsable.nomUser,
                    "cargo": responsable.cargo,
                    "area": responsable.area
                },
            }
            if reporte.evidencia_atendido:
                evidencia_atendido = json.loads(base64.b64decode(reporte.evidencia_atendido).decode("UTF-8"))
                data["evidencia_atendido"] = {
                    "evidencia_1": evidencia_atendido["evidencia_1"],
                    "evidencia_2": evidencia_atendido["evidencia_2"],
                    "evidencia_3": evidencia_atendido["evidencia_3"],
                }
            else:
                data["evidencia_atendido"] = "null"
            return True, data
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

    def actualizar_estado(self,
                          id_reporte: int,
                          estado: str):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
            if reporte:
                reporte.estado = estado
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

    def reasignar(self,
                  id_reporte: int,
                  responsable: int):
        try:
            reporte = self.db.query(Reportes).filter(Reportes.ID_report == id_reporte).first()
            if reporte:
                reporte.responsable = responsable
                self.db.commit()
                return True, {"status": 1, "detail": "Succesful Update"}
            else:
                return True, {"status": 0, "detail": "Reporte not found"}
        except Exception as err:
            print(err)
            return False, {"status": 0, "detail": err}

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
                    usuario = self.db.query(Usuario).filter(Usuario.ID_user == token_data.id_usuario)
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

    def authToken(self, token):
        try:
            token = self.db.query(SessionTokens).filter(SessionTokens.token == token).first()
            expiration_date = parse(str(token.expiration))
            today = parse(str(datetime.today()))
            if token.expirated == 0:
                if today < expiration_date:
                    new_expiration_date = datetime.now() + timedelta(days=30)
                    token.expiration = new_expiration_date
                    self.db.commit()
                    return False, {"status": 1, "detail": "Token valido"}
                else:
                    token.expirated = 1
                    self.db.commit()
                    return False, {"status": 0, "detail": "Token expirado"}
            else:
                return False, {"status": 2, "detail": "Token expirado"}
            pass
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
