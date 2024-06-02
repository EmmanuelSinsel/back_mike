import datetime

from fastapi import APIRouter, FastAPI, Depends, Response, Header
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from models import *

from repositories import *

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# lo siguiente solo se va a poner para cuando este hosteado en el OracleCloud
# app = FastAPI(root_path="/backend-fim")

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

usuarios = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

reportes = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

areas = APIRouter(
    prefix="/areas",
    tags=["Areas"]
)

categorias = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)

auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# BASES DE DATOS
@usuarios.post("/registrar_escuela")
def registrar(*,
              data: RegistrarEscuela,
              response: Response):
    service = Repo(database="fim_main")
    status, res = service.registrar_escuela(data=data)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res



# USUARIOS
@usuarios.get("/login")
def login(*,
          usuario: str,
          password: str,
          response: Response):
    service = Repo(database="fim_main")
    status, res = service.login(no_cuenta=usuario,
                                password=password)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@usuarios.post("/registrar_usuario")
def registrar(*,
              data: RegistrarUsuario,
              response: Response):
    service = Repo(database="main_fim")
    status, res = service.registrar(data=data)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res


@usuarios.post("/reasignar_area")
def reasignar(*,
              id_usuario: int,
              area: str,
              tipoUser: str,
              response: Response,
              school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.reasignar_area(id_usuario=id_usuario, area=area, tipoUser=tipoUser)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res


@usuarios.get("/detalle_usuario")
def generar_reporte(*,
                    id_usuario: int,
                    response: Response,
                    school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.detalle_usuario(id_usuario=id_usuario)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res


# REPORTES
@reportes.post("/registrar_reporte")
def generar_reporte(*,
                    data: RegistrarReporte,
                    response: Response,
                    school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.generar_reporte(data=data)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res


@reportes.get("/historial_reportes")
def ver_historial(*,
                  id_usuario: int,
                  estatus: str = None,
                  tipo_report: str = None,
                  urgencia: bool = True,
                  response: Response,
                  school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.ver_historial(id_usuario=id_usuario,
                                        estatus=estatus,
                                        tipo_report=tipo_report,
                                        urgencia=urgencia)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.get("/historial_reportes_responsable")
def ver_historial_responsable(*,
                              id_usuario: int,
                              estatus: str = None,
                              tipo_report: str = None,
                              urgencia: bool = True,
                              response: Response,
                              school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.ver_historial_responsable(id_responsable=id_usuario,
                                                    estatus=estatus,
                                                    tipo_report=tipo_report,
                                                    urgencia=urgencia)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.delete("/eliminar_reporte")
def eliminar_reporte(*,
                     id_reporte: int,
                     response: Response,
                     school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.eliminar_reporte(id_reporte=id_reporte)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.patch("/repostear_reporte")
def repostear_reporte(*,
                      id_reporte: int,
                      response: Response,
                      school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.repostear_reporte(id_reporte=id_reporte)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.get("/lista_reportes")
def ver_reportes(*,
                 estatus: str = 'Pendiente',
                 tipo_report: str = None,
                 urgencia: bool = False,
                 sin_asignar: bool = False,
                 response: Response,
                 school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.ver_reportes(estatus=estatus,
                                       tipo_report=tipo_report,
                                       urgencia=urgencia,
                                       sin_asignar=sin_asignar)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.get("/detalle_reporte")
def ver_detalles(*,
                 id_reporte: int,
                 response: Response,
                 school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.ver_detalles(id_reporte=id_reporte)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.patch("/actualizar_estado")
def actualizar_estado(*,
                      id_reporte: int,
                      estado: str,
                      response: Response,
                      school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.actualizar_estado(id_reporte=id_reporte, estado=estado)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.patch("/reasignar_reporte")
def reasignar(*,
              id_reporte: int,
              area: str,
              ID_user: int,
              response: Response,
              school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.reasignar(id_reporte=id_reporte, area=area, ID_user=ID_user)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.put("/evidencias_atendido")
def evidencias_atendido(*,
                        id_reporte: int,
                        data: EvidenciasAtendido,
                        response: Response,
                        school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.evidencias_atendido(id_reporte=id_reporte, data=data)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@usuarios.get("/lista_usuarios")
def lista_usuarios(*,
                   response: Response,
                   school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.lista_usuarios()
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@usuarios.get("/lista_usuarios_area")
def lista_usuarios_area(*,
                        area: str,
                        response: Response,
                        school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.lista_usuarios_area(area=area)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@auth.get("/verificar_cuenta")
def verificar_cuenta(*,
                     token: str,
                     response: Response,
                     school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.verificarToken(token=token)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@auth.get("/enviar_correo_password_reset")
def enviar_correo_password_reset(*,
                                 email: str,
                                 id_usuario: int,
                                 response: Response,
                                 school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.enviarCorreoPasswordReset(email=email,
                                                    id_usuario=id_usuario)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@auth.get("/password_reset")
def password_reset(*,
                   token: str,
                   new_password: str,
                   response: Response,
                   school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.passwordReset(token=token,
                                        new_password=new_password)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@categorias.get("/lista_categorias")
def lista_categorias(
        response: Response,
        school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.lista_categorias()
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@categorias.post("/registrar_categoria")
def registrar_categoria(*,
                        categoria: RegistrarCategoria,
                        response: Response,
                        school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.registrar_categoria(categoria=categoria)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res


@categorias.delete("/eliminar_categoria")
def eliminar_categoria(*,
                       id_categoria: int,
                       response: Response,
                       school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.eliminar_categoria(id_categoria=id_categoria)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@categorias.put("/actualizar_categoria")
def actualizar_categoria(*,
                         id_categoria: int,
                         categoria: RegistrarCategoria,
                         response: Response,
                         school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.actualizar_categoria(id_categoria=id_categoria,
                                               categoria=categoria)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@areas.get("/lista_areas")
def lista_areas(
        response: Response,
        school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.lista_areas()
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@areas.post("/registrar_area")
def registrar_area(*,
                   area: RegistrarArea,
                   response: Response,
                   school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.registrar_area(area=area)
    service.db.close()
    if status:
        response.status_code = 201
    else:
        response.status_code = 501
    return res


@areas.delete("/eliminar_area")
def eliminar_area(*,
                  id_area: int,
                  response: Response,
                  school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.eliminar_area(id_area=id_area)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@areas.put("/actualizar_area")
def actualizar_area(*,
                    id_area: int,
                    area: RegistrarArea,
                    response: Response,
                    school: Annotated[str | None, Header()] = None):
    service = Repo(database=school)
    status, res = service.actualizar_area(id_area=id_area
                                          , area=area)
    service.db.close()
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


app.include_router(usuarios)
app.include_router(reportes)
app.include_router(auth)
app.include_router(areas)
app.include_router(categorias)
