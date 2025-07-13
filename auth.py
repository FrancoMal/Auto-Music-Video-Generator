import tkinter as tk
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Funciones para la autenticación y manejo de sesiones
# Constantes
SCOPES = ['https://www.googleapis.com/auth/youtube']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.pickle'


# def actualizar_ui_con_nombre_canal(nombre_canal):
#    if nombre_canal:
#       label_nombre_canal.config(text=nombre_canal)
#    else:
#       label_nombre_canal.config(
#            text="No se pudo obtener el nombre del canal")

def obtener_credenciales():
    """
    Carga o genera credenciales necesarias para acceder a la API de YouTube.
    Devuelve un objeto de credenciales.
    """
    creds = None
    # Intenta cargar credenciales existentes
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Si no hay credenciales válidas disponibles, permite al usuario iniciar sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guarda las credenciales para el próximo inicio de sesión
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def iniciar_sesion():
    creds = None
    # Cargar credenciales si ya existen
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Si no hay credenciales válidas, hacer el flujo de autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar las credenciales para la próxima ejecución
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    nombre_canal = obtener_nombre_canal(creds)
    # actualizar_ui_con_nombre_canal(nombre_canal)
    return creds, nombre_canal


def cerrar_sesion():
    # Eliminar el archivo token
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    # No hay necesidad de actualizar la interfaz de usuario aquí
    print("Sesión cerrada con éxito")


def verificar_sesion():
    # Verifica si hay una sesión activa
    pass


def obtener_nombre_canal(credentials):
    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()
        if response['items']:
            return response['items'][0]['snippet']['title']
    except Exception as e:
        print(
            f"Error al construir el cliente de la API o al realizar la solicitud: {e}")
        # Aquí podrías poner más lógica de manejo de errores si es necesario
        return None
