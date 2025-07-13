import tkinter as tk
from tkinter import ttk, Label, Entry, Button, Spinbox, Listbox, Toplevel, filedialog
from tkcalendar import Calendar
import os
from datetime import datetime, timedelta
import upload_video
import auth
from tkinter import ttk
from auth import obtener_credenciales
from upload_video import upload_video
from googleapiclient.discovery import build
import pytz
import shutil


root = tk.Tk()
root.title("Subidor de Videos a YouTube")
output_folder_path = ""

lista_videos = []  # Lista para almacenar los nombres de los videos
lista_videos_programados = []
creds = obtener_credenciales()
# Función que abre el calendario para seleccionar la fecha
youtube = build('youtube', 'v3', credentials=creds)
categorias = {
    "Videojuegos": "20",
    # ... puedes agregar más categorías según necesites
}

titulo_entry = tk.Entry(root)
numero_inicial_spinbox = tk.Spinbox(root, from_=1, to=1000)
categoria_combobox = ttk.Combobox(root)
etiquetas_entry = tk.Entry(root)
descripcion_entry = tk.Entry(root)


def seleccionar_carpeta_destino():
    global output_folder_path
    output_folder_path = filedialog.askdirectory()
    if output_folder_path:
        print(f"La carpeta de destino seleccionada es: {output_folder_path}")
    else:
        print("No se seleccionó ninguna carpeta de destino.")


def mover_y_renombrar_archivo(original_path, video_id, publish_time):
    if not output_folder_path:
        print("No se ha seleccionado una carpeta de destino.")
        return

    # Construye el nuevo nombre de archivo con la fecha y hora de subida
    nuevo_nombre = f"Video_{publish_time}.mp4"
    nuevo_path = os.path.join(output_folder_path, nuevo_nombre)

    # Mueve y renombra el archivo
    shutil.move(original_path, nuevo_path)
    print(f"Archivo movido a {nuevo_path}")


def convertir_hora_local_a_utc_rfc3339(fecha, hora, zona_horaria_local='America/Argentina/Buenos_Aires'):
    # Combina la fecha y la hora en una sola cadena y conviértela a un objeto datetime
    fecha_hora_local = datetime.strptime(f'{fecha} {hora}', '%Y-%m-%d %H:%M')

    # Localiza la fecha y hora en la zona horaria especificada
    local = pytz.timezone(zona_horaria_local)
    local_dt = local.localize(fecha_hora_local, is_dst=None)

    # Convierte la fecha y hora local a UTC
    utc_dt = local_dt.astimezone(pytz.utc)

    # Devuelve la fecha y hora en formato RFC 3339
    return utc_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

# Función para convertir la categoría legible por humanos a su ID correspondiente


def convertir_categoria_a_id(categoria):
    categorias = {
        "Videojuegos": "20",
        # ... otros mapeos de categorías ...
    }
    if categoria not in categorias:
        raise ValueError(f"Categoría '{categoria}' no encontrada")
    return categorias[categoria]


def upload_video_callback():
    # Iterar sobre la lista de videos programados para subirlos
    for video_info in lista_videos_programados:
        categoria_id = 20
        if not categoria_id:
            print(
                f"Error: La categoría {categoria_combobox.get()} no es válida.")
            continue

        resultado, error = upload_video(
            creds,
            video_info['path'],
            video_info['titulo'],
            descripcion_entry.get(),
            categoria_id,
            etiquetas_entry.get(),
            "private",  # Asumiendo que todos los videos son privados al principio
            video_info['publish_at']
        )

        if error:
            print(f"Error al subir el video {video_info['titulo']}: {error}")
        else:
            print(
                f"Video {video_info['titulo']} subido correctamente con el ID: {resultado['id']}")

        if not error:
            # ... (Código que se ejecuta después de una subida exitosa)
            # Obtén la hora de publicación en formato adecuado
            publish_time = video_info['publish_at'].replace(
                ':', '-').replace('.', '-')
            # Mueve y renombra el archivo
            mover_y_renombrar_archivo(
                video_info['path'], resultado['id'], publish_time)
# Ahora, definimos `comenzar_subida` que manejará la lógica de la subida


def comenzar_subida(titulo_base, numero_serie, categoria, etiquetas, descripcion, privacy_status):
    # Obtener las credenciales para la API de YouTube
    creds = obtener_credenciales()
    if not creds:
        print("Error al obtener las credenciales. Por favor, inicie sesión.")
        return

    # Iterar sobre la lista de videos programados para subirlos
    for video_info in lista_videos_programados:
        # Reemplazar {} con el número de serie actual en el título base
        titulo_video = titulo_base.replace("{}", str(numero_serie))
        numero_serie += 1  # Incrementar para el próximo video

        # Llama a la función que realiza la subida del video
        resultado, error = upload_video(
            creds, video_info['path'], titulo_video, descripcion,
            categoria, etiquetas.split(
                ','), privacy_status, video_info['publish_at']
        )

        if error:
            print(f"Error al subir el video {titulo_video}: {error}")
        else:
            print(
                f"Video {titulo_video} subido correctamente con el ID: {resultado['id']}")

# Suponiendo que obtener_credenciales y subir_video_a_youtube están definidas así:


def obtener_credenciales():
    # Esta función obtendría las credenciales guardadas o haría que el usuario iniciara sesión
    # y devolvería un objeto credentials
    pass


def iniciar_sesion_callback():
    global label_estado_sesion
    creds, nombre_canal = auth.iniciar_sesion()
    if nombre_canal:
        label_estado_sesion.config(text=f"Logueado como: {nombre_canal}")
    else:
        label_estado_sesion.config(text="Inicio de sesión fallido")


def cerrar_sesion_callback():
    auth.cerrar_sesion()
    label_estado_sesion.config(text="Sesión cerrada")


def abrir_calendario(entrada_texto):
    def establecer_fecha():
        entrada_texto.delete(0, tk.END)
        entrada_texto.insert(0, calendario.get_date())
        ventana_calendario.destroy()

    ventana_calendario = Toplevel(root)
    calendario = Calendar(ventana_calendario,
                          selectmode='day', date_pattern='dd/mm/yyyy')
    calendario.pack(pady=20)
    Button(ventana_calendario, text="Seleccionar",
           command=establecer_fecha).pack()

# Función para generar intervalos de tiempo de 15 minutos


def generar_intervalos_tiempo():
    intervalos = []
    for hora in range(24):
        for minuto in [0, 15, 30, 45]:
            intervalos.append(f"{hora:02d}:{minuto:02d}")
    return intervalos

# Función para seleccionar carpeta y actualizar la lista de videos


def seleccionar_carpeta():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        # Obtiene solo los nombres de archivo de los videos, sin la ruta completa
        videos = [file for file in os.listdir(
            folder_selected) if file.lower().endswith(('.mp4', '.avi', '.mov'))]
        # Agrega la ruta completa para uso interno
        lista_videos.extend([os.path.join(folder_selected, file)
                            for file in videos])
        # Actualiza el Listbox con los nombres de archivo
        carpetas_listbox.delete(0, tk.END)  # Limpia el Listbox actual
        for video in videos:
            # Agrega el nombre de archivo al Listbox
            carpetas_listbox.insert(tk.END, video)
        actualizar_contador_videos()
# Función para actualizar el contador de videos


def actualizar_contador_videos():
    total_videos = len(lista_videos)
    contador_videos.config(text=f"Total de Videos: {total_videos}")

# Función para abrir la ventana de programación de subida


def abrir_ventana_programacion():
    ventana_programacion = Toplevel(root)
    ventana_programacion.title("Programar Subida de Videos")
    ventana_programacion.geometry("600x400")
    ventana_programacion.minsize(600, 400)

    global numero_inicial

    # Lista para almacenar los widgets de horarios
    horarios_entries = []
    entrada_desde = Entry(ventana_programacion)
    entrada_hasta = Entry(ventana_programacion)
    # Listbox para la vista previa
    listbox_vista_previa = Listbox(ventana_programacion, width=50, height=10)
    listbox_vista_previa.grid(
        row=13, column=1, columnspan=2, rowspan=4, pady=5, sticky='ew')

    def actualizar_horarios():
        nonlocal horarios_entries
        for widget in horarios_entries:
            widget.destroy()
        horarios_entries.clear()

        intervalos = generar_intervalos_tiempo()
        for i in range(int(spb_videos_por_dia.get())):
            label_horario = ttk.Label(
                ventana_programacion, text=f"Horario {i+1}")
            label_horario.grid(row=i+1, column=0)
            combobox_horario = ttk.Combobox(
                ventana_programacion, values=intervalos, state="readonly")
            combobox_horario.grid(row=i+1, column=1)
            combobox_horario.set("00:00")
            horarios_entries.append(combobox_horario)

    # Función para mostrar la vista previa de los videos a subir
# Función para mostrar la vista previa de los videos a subir y preparar la lista de videos programados
    def mostrar_vista_previa():
        global lista_videos_programados
        lista_videos_programados.clear()  # Limpia la lista actual

        fecha_inicio = datetime.strptime(entrada_desde.get(), '%d/%m/%Y')
        fecha_fin = datetime.strptime(entrada_hasta.get(), '%d/%m/%Y')
        delta = fecha_fin - fecha_inicio

        numero_serie = int(numero_inicial.get())
        for i in range(delta.days + 1):
            fecha_actual = fecha_inicio + timedelta(days=i)
            for horario_widget in horarios_entries:
                horario = horario_widget.get()
                indice_video = numero_serie - int(numero_inicial.get())
                if indice_video < len(lista_videos):
                    ruta_video = lista_videos[indice_video]
                    titulo_video = titulo.get().replace("{}", str(numero_serie))
                    lista_videos_programados.append({
                        'path': ruta_video,  # Asegúrate de que esta sea la ruta completa al archivo
                        'titulo': titulo_video,
                        'fecha': fecha_actual.strftime('%Y-%m-%d'),
                        'hora': horario,
                        'publish_at': convertir_hora_local_a_utc_rfc3339(fecha_actual.strftime('%Y-%m-%d'), horario)
                    })
                    numero_serie += 1

        # Actualizar la vista previa en la interfaz de usuario
        listbox_vista_previa.delete(0, tk.END)  # Limpia el Listbox
        for video_info in lista_videos_programados:
            listbox_vista_previa.insert(
                tk.END, f"{video_info['fecha']} {video_info['hora']} - {video_info['titulo']}")
    # Función que se llamará al presionar el botón "Aceptar"

    def obtener_credenciales_tiktok():
        # Esta función obtendría las credenciales guardadas o haría que el usuario iniciara sesión
        # y devolvería un objeto credentials para TikTok
        pass

    def iniciar_sesion_tiktok_callback():
        try:
            creds_tiktok = obtener_credenciales_tiktok()
            if creds_tiktok:
                label_estado_sesion_tiktok.config(text="Logueado en TikTok.")
            else:
                label_estado_sesion_tiktok.config(
                    text="Inicio de sesión en TikTok fallido.")
        except Exception as e:
            label_estado_sesion_tiktok.config(text=f"Error: {e}")

    def cerrar_sesion_tiktok_callback():
        try:
            # Lógica para invalidar el token de acceso de TikTok y borrar 'tiktok_token.pickle'
            label_estado_sesion_tiktok.config(text="Sesión en TikTok cerrada.")
        except Exception as e:
            label_estado_sesion_tiktok.config(text=f"Error: {e}")

    # Widget para seleccionar la cantidad de videos por día
    Label(ventana_programacion, text="Videos por día").grid(row=0, column=0)
    spb_videos_por_dia = Spinbox(
        ventana_programacion, from_=1, to=10, command=actualizar_horarios)
    spb_videos_por_dia.grid(row=0, column=1)

    # Entrada y botón para la fecha 'Desde'
    Label(ventana_programacion, text="Desde").grid(row=11, column=0)
    entrada_desde = Entry(ventana_programacion)
    entrada_desde.grid(row=11, column=1)
    Button(ventana_programacion, text="Seleccionar Fecha",
           command=lambda: abrir_calendario(entrada_desde)).grid(row=11, column=2)

    # Entrada y botón para la fecha 'Hasta'
    Label(ventana_programacion, text="Hasta").grid(row=12, column=0)
    entrada_hasta = Entry(ventana_programacion)
    entrada_hasta.grid(row=12, column=1)
    Button(ventana_programacion, text="Seleccionar Fecha",
           command=lambda: abrir_calendario(entrada_hasta)).grid(row=12, column=2)

    # Listbox para vista previa
    Label(ventana_programacion, text="Vista previa").grid(
        row=13, column=0, pady=5)
    listbox_vista_previa = Listbox(ventana_programacion, width=50, height=10)
    listbox_vista_previa.grid(
        row=13, column=1, columnspan=2, rowspan=4, pady=5, sticky='ew')

    # Botones para actualizar vista previa y comenzar la subida
    Button(ventana_programacion, text="Actualizar Vista Previa",
           command=mostrar_vista_previa).grid(row=18, column=0, columnspan=2, pady=10)
    # Botones y etiquetas para la sesión de TikTok
# Botones y etiquetas para la sesión de TikTok
    boton_iniciar_tiktok = Button(
        ventana_programacion, text="Iniciar Sesión en TikTok", command=iniciar_sesion_tiktok_callback)
    boton_iniciar_tiktok.grid(row=19, column=0, pady=10)
    boton_cerrar_tiktok = Button(
        ventana_programacion, text="Cerrar Sesión en TikTok", command=cerrar_sesion_tiktok_callback)
    boton_cerrar_tiktok.grid(row=19, column=1, pady=10)
    label_estado_sesion_tiktok = Label(
        ventana_programacion, text="Estado de la sesión de TikTok aquí")
    label_estado_sesion_tiktok.grid(row=19, column=2, pady=10)

    Button(ventana_programacion, text="Aceptar", command=upload_video_callback).grid(
        row=20, column=0, columnspan=3, pady=10)


# Botones y etiquetas para la sesión
boton_iniciar = tk.Button(root, text="Iniciar Sesión",
                          command=iniciar_sesion_callback)
boton_iniciar.pack()
boton_cerrar = tk.Button(root, text="Cerrar Sesión",
                         command=cerrar_sesion_callback)
boton_cerrar.pack()
label_estado_sesion = tk.Label(root, text="Estado de la sesión aquí")
label_estado_sesion.pack()

# Botón para seleccionar carpetas y mostrar las carpetas seleccionadas
boton_seleccionar = Button(
    root, text="Seleccionar Carpeta de Videos", command=seleccionar_carpeta)
boton_seleccionar.pack()
boton_seleccionar_destino = Button(
    root, text="Seleccionar Carpeta de Destino", command=seleccionar_carpeta_destino)
boton_seleccionar_destino.pack()
# Etiqueta y Listbox para mostrar las carpetas seleccionadas
carpetas_listbox = Listbox(root)
carpetas_listbox.pack()

# Etiqueta para mostrar la cantidad total de videos
contador_videos = Label(root, text="Total de Videos: 0")
contador_videos.pack()

# Campo para título con espacio para el número de serie
Label(root, text="Título (incluye un espacio para el número):").pack()
titulo = Entry(root)
titulo.insert(
    0, "Skarner Rework 🦂🦂#{} #skarner #leagueoflegends #shorts #leagueoflegendsclips #lol #top #rework #jg")
titulo.pack()


# Campo para el número inicial de la serie
Label(root, text="Número Inicial para la Serie:").pack()
numero_inicial = Spinbox(root, from_=1, to=1000)
numero_inicial.pack()

# Añade un menú desplegable para la selección de categoría
categoria_label = tk.Label(root, text="Categoría:")
categoria_label.pack()
categoria_var = tk.StringVar(value='Videojuegos')  # Valor predeterminado
categoria_menu = ttk.Combobox(root, textvariable=categoria_var, values=list(
    categorias.keys()), state="readonly")
categoria_menu.pack()

etiquetas_default = "aram,aram fun,aram league,aram league of legends,aram pentakill,faker,franxxkito,fun aram,gaming,league of legends,lol,lol montage,master,op,pentakill,skarner,skarner blindaje alfa,skarner jg,skarner manamune,skarner op,skarner rework,skarner top,skill,tank,wave managment"

etiquetas_label = tk.Label(root, text="Etiquetas (separadas por comas):")
etiquetas_label.pack()
etiquetas_entry = tk.Entry(root)
etiquetas_entry.insert(0, etiquetas_default)  # Insertar valor predeterminado
etiquetas_entry.pack()

descripcion_default = "Skarner Rewrok Shorts Series | SRSS | Skarner Top\nLeague of Legends - Master\nhttps://www.leagueofgraphs.com/summoner/las/FranxxKito"

descripcion_label = tk.Label(root, text="Descripcion:")
descripcion_label.pack()
# Usar widget Text para múltiples líneas
descripcion_entry = tk.Entry(root)
# Insertar valor predeterminado
descripcion_entry.insert(0, descripcion_default)
descripcion_entry.pack()

# Botón para programar la subida
Button(root, text="Programar Subida", command=abrir_ventana_programacion).pack()


root.mainloop()
