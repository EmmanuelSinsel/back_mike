import datetime

from fastapi import APIRouter, FastAPI, Depends, Response
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from models import *

from repositories import *

app = FastAPI()

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     headers = dict(request.scope['headers'])
#     base = str(request.base_url)
#     url = str(request.url)
#     excluded_urls = ["api/login",
#                      "api/password_recover",
#                      "api/password_reset",
#                      "api/verify_email",
#                      "api/send_email_verification",
#                      "api/password_token_verify",
#                      "api/authenticate"]
#     if b'access-control-request-headers' in headers:
#         response = await call_next(request)
#         return response
#     if base in url:
#         url = url.replace(base, '')
#     if url == "docs" or url == "openapi.json":
#         response = await call_next(request)
#         return response
#     elif url in excluded_urls:
#         response = await call_next(request)
#         return response
#     else:
#         try:
#             token = request.headers.get('token')
#             auth = Repo()
#             if url == "login":
#                 response = await call_next(request)
#                 headers = {"Access-Control-Allow-Origin": "*"}
#                 return JSONResponse(content=response, headers=headers)
#             elif token == "":
#                 response = {"status": "401", "msg": "Not logged"}
#                 return JSONResponse(content=response)
#             elif auth.verificarToken(token):
#                 response = await call_next(request)
#                 headers = {"Access-Control-Allow-Origin": "*"}
#                 return JSONResponse(content=response, headers=headers)
#             else:
#                 response = {"status": "401", "msg": "Invalid token"}
#                 return JSONResponse(content=response)
#         except:
#             return response

usuarios = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

reportes = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# USUARIOS
@usuarios.get("/login")
def login(*,
          usuario: str,
          password: str,
          response: Response,
          service: Annotated[Repo, Depends()]):
    status, res = service.login(usuario=usuario,
                                password=password)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@usuarios.post("/registrar_usuario")
def registrar(*,
              data: RegistrarUsuario,
              response: Response,
              service: Annotated[Repo, Depends()]):
    status, res = service.registrar(data=data)
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
                    service: Annotated[Repo, Depends()]):
    status, res = service.generar_reporte(data=data)
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
                  urgencia: bool = False,
                  response: Response,
                  service: Annotated[Repo, Depends()]):
    status, res = service.ver_historial(id_usuario=id_usuario,
                                        estatus=estatus,
                                        tipo_report=tipo_report,
                                        urgencia=urgencia)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.delete("/eliminar_reporte")
def eliminar_reporte(*,
                     id_reporte: int,
                     response: Response,
                     service: Annotated[Repo, Depends()]):
    status, res = service.eliminar_reporte(id_reporte=id_reporte)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.patch("/repostear_reporte")
def repostear_reporte(*,
                      id_reporte: int,
                      response: Response,
                      service: Annotated[Repo, Depends()]):
    status, res = service.repostear_reporte(id_reporte=id_reporte)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.get("/lista_reportes")
def ver_reportes(*,
                 estatus: str = None,
                 tipo_report: str = None,
                 urgencia: bool = False,
                 response: Response,
                 service: Annotated[Repo, Depends()]):
    status, res = service.ver_reportes(estatus=estatus,
                                       tipo_report=tipo_report,
                                       urgencia=urgencia)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


@reportes.get("/detalle_reporte")
def ver_detalles(*,
                 id_reporte: int,
                 response: Response,
                 service: Annotated[Repo, Depends()]):
    status, res = service.ver_detalles(id_reporte=id_reporte)
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
                      service: Annotated[Repo, Depends()]):
    status, res = service.actualizar_estado(id_reporte=id_reporte, estado=estado)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res

@reportes.patch("/reasignar_reporte")
def reasignar(*,
              id_reporte: int,
              responsable: int,
              response: Response,
              service: Annotated[Repo, Depends()]):
    status, res = service.reasignar(id_reporte=id_reporte, responsable=responsable)
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
                        service: Annotated[Repo, Depends()]):
    status, res = service.evidencias_atendido(id_reporte=id_reporte, data=data)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res

@auth.get("/verificar_cuenta")
def verificar_cuenta(*,
                        token: str,
                        response: Response,
                        service: Annotated[Repo, Depends()]):
    status, res = service.verificarToken(token=token)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res

@auth.get("/enviar_correo_password_reset")
def enviar_correo_password_reset(*,
                     email:str,
                     id_usuario: int,
                     response: Response,
                     service: Annotated[Repo, Depends()]):
    status, res = service.enviarCorreoPasswordReset(email=email,
                                                    id_usuario=id_usuario)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res

@auth.get("/password_reset")
def password_reset(*,
                     token:str,
                     new_password: str,
                     response: Response,
                     service: Annotated[Repo, Depends()]):
    status, res = service.passwordReset(token=token,
                                        new_password=new_password)
    if status:
        response.status_code = 200
    else:
        response.status_code = 501
    return res


app.include_router(usuarios)
app.include_router(reportes)
app.include_router(auth)

