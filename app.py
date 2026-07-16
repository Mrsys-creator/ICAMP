import sys
import os
import re
import subprocess

def obtener_ruta_recurso(nombre_archivo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_archivo)
    return os.path.join(os.path.abspath("."), nombre_archivo)

import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import io

import urllib.request
import json
import threading
import time

# ============================================
# 🚀 SISTEMA DE ACTUALIZACIONES AUTOMÁTICAS
# ============================================

class Actualizador:
    """Maneja las actualizaciones automáticas del programa"""
    
    # ===== ⚙️ CONFIGURACIÓN =====
    URL_VERSION = "https://raw.githubusercontent.com/Mrsys-creator/ICAMP/refs/heads/main/version.json"
    VERSION_ACTUAL = "1.0.2"
    NOMBRE_APP = "Renombrador PDF"
    
    @staticmethod
    def verificar_actualizacion(parent=None):
        try:
            req = urllib.request.Request(
                Actualizador.URL_VERSION,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            version_remota = data.get("version", "0.0.0")
            url_descarga = data.get("app_url", "")
            mensaje = data.get("mensaje", "Nueva versión disponible")
            
            if Actualizador._es_version_mayor(version_remota, Actualizador.VERSION_ACTUAL):
                respuesta = messagebox.askyesno(
                    f"📦 {Actualizador.NOMBRE_APP} - Actualización disponible",
                    f"🔔 Nueva versión **{version_remota}** disponible.\n\n"
                    f"📌 Cambios:\n{mensaje}\n\n"
                    f"¿Deseas descargar e instalar la actualización ahora?\n\n"
                    f"(El programa se reiniciará automáticamente)"
                )
                
                if respuesta:
                    return Actualizador._descargar_actualizacion(url_descarga, parent)
            
            return False
            
        except Exception as e:
            print(f"Error al verificar actualización: {e}")
            return False
    
    @staticmethod
    def _es_version_mayor(version1, version2):
        try:
            v1 = [int(x) for x in version1.split('.')]
            v2 = [int(x) for x in version2.split('.')]
            
            while len(v1) < len(v2):
                v1.append(0)
            while len(v2) < len(v1):
                v2.append(0)
            
            for i in range(len(v1)):
                if v1[i] > v2[i]:
                    return True
                elif v1[i] < v2[i]:
                    return False
            return False
        except:
            return version1 > version2
    
    @staticmethod
    def _descargar_actualizacion(url, parent=None):
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            temp_file = os.path.join(base_dir, "app_nuevo.py")
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(temp_file, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            
            app_actual = os.path.join(base_dir, "app.py")
            
            backup_file = os.path.join(base_dir, "app_backup.py")
            if os.path.exists(app_actual):
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(app_actual, backup_file)
            
            os.rename(temp_file, app_actual)
            
            messagebox.showinfo(
                "✅ Actualización completada",
                f"La aplicación se ha actualizado correctamente.\n\n"
                f"El programa se reiniciará automáticamente."
            )
            
            def reiniciar():
                if getattr(sys, 'frozen', False):
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    os.execl(sys.executable, sys.executable, *sys.argv)
            
            threading.Timer(1.5, reiniciar).start()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo descargar la actualización:\n\n{str(e)}")
            return False

def verificar_actualizacion_al_inicio():
    splash = tk.Toplevel()
    splash.title("")
    splash.geometry("300x100")
    splash.overrideredirect(True)
    
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 100) // 2
    splash.geometry(f"+{x}+{y}")
    
    tk.Label(
        splash, 
        text="🔍 Verificando actualizaciones...", 
        font=("Arial", 12)
    ).pack(expand=True)
    splash.update()
    
    def verificar():
        time.sleep(0.5)
        splash.destroy()
        Actualizador.verificar_actualizacion()
    
    threading.Thread(target=verificar, daemon=True).start()

# FUNCIÓN: Ordenamiento natural
def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

ETIQUETAS = {
    "IESS": {
        "AMB": [
            "2. COBERTURA DE SALUD",
            "3. CODIGO DE VALIDACION",
            "4. FORMULARIO 053",
            "5. FORMULARIO 007",
            "6. FORMULARIO 002",
            "7. FORMULARIO 012",
            "HOJA BLANCA"
        ],
        "HD": [
            "2. COBERTURA DE SALUD",
            "3. CODIGO DE VALIDACION",
            "4. FORMULARIO 053",
            "5. FORMULARIO 007",
            "6. FORMULARIO 006",
            "7. ACTA ENTREGA RECEPCION",
            "8. PROTOCOLO OPERATORIO",
            "9. REGISTRO DE ANESTESIA",
            "10. NOTA DE INGRESO EGRESO",
            "11. FACTURAS",
            "HOJA BLANCA"
        ],
        "UNIDO": [
            "1. PLANILLA INDIVIDUAL",
            "2. CÓDIGO DE VALIDACIÓN",
            "3. COBERTURA DE SALUD",
            "4. FORMULARIO 053",
            "5. FORMULARIO 007",
            "6. FORMULARIO 002",
            "7. FORMULARIO 012A",
            "8. FORMULARIO 012B",
            "9. PROTOCOLO QUIRÚRGICO 017",
            "10. PROTOCOLO ANESTÉSICO 018",
            "11. ACTA DE ENTREGA",
            "12. EPICRISIS 006",
            "13. ANEXOS",
            "HOJA BLANCA"
        ]
    },
    "ISSFA": {
        "AMB": [
            "1. ORDEN DE ATENCIÓN",
            "2. CERTIFICADO MÉDICO",
            "3. FORMULARIO 101",
            "HOJA BLANCA"
        ],
        "HD": [
            "1. HISTORIA CLÍNICA",
            "2. NOTA DE EVOLUCIÓN",
            "3. FACTURA DETALLADA",
            "HOJA BLANCA"
        ],
        "UNIDO": [
            "1. PLANILLA INDIVIDUAL",
            "2. CÓDIGO DE VALIDACIÓN",
            "3. COBERTURA DE SALUD",
            "4. FORMULARIO 053",
            "5. FORMULARIO 007",
            "6. FORMULARIO 002",
            "7. FORMULARIO 012A",
            "8. FORMULARIO 012B",
            "9. PROTOCOLO QUIRÚRGICO 017",
            "10. PROTOCOLO ANESTÉSICO 018",
            "11. ACTA DE ENTREGA",
            "12. EPICRISIS 006",
            "13. ANEXOS",
            "HOJA BLANCA"
        ]
    }
}

class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renombrador PDF")
        self.root.geometry("1000x650")

        self.tipo_var = tk.StringVar(value="AMB")
        self.institucion_var = tk.StringVar()

        self.pdfs = []
        self.pdf_index = -1
        self.page_index = 0
        self.page_etiquetas = {}
        self.deleted_pages = set()
        self.rotacion_actual = {}
        self.orden_paginas = []

        self.total_pdfs = 0
        self.actual_pdf = 0

        self.doc = None
        self.path_pdf = None

        # Frames principales
        self.menu_frame = tk.Frame(self.root, width=1000, height=600)
        self.menu_frame.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.root, width=1000, height=600)

        self.crear_menu_inicio()
    
        # ===== VERIFICAR ACTUALIZACIONES AL INICIAR =====
        verificar_actualizacion_al_inicio()

    def crear_menu_inicio(self):
        self.canvas_menu = tk.Canvas(self.menu_frame, width=1000, height=600)
        self.canvas_menu.pack(fill="both", expand=True)

        try:
            self.img_iess = Image.open(obtener_ruta_recurso("fondo_iess.png")).resize((400, 400))
            self.tk_img_iess = ImageTk.PhotoImage(self.img_iess)
        except:
            self.tk_img_iess = None
            
        try:
            self.img_issfa = Image.open(obtener_ruta_recurso("fondo_issfa.png")).resize((400, 400))
            self.tk_img_issfa = ImageTk.PhotoImage(self.img_issfa)
        except:
            self.tk_img_issfa = None

        self.iess_pos_x = 250
        self.issfa_pos_x = 750

        if self.tk_img_iess:
            self.canvas_menu.create_image(self.iess_pos_x, 200, image=self.tk_img_iess)
        else:
            self.canvas_menu.create_rectangle(50, 50, 450, 450, fill="#005B9F", outline="white", width=3)
            self.canvas_menu.create_text(250, 250, text="IESS", fill="white", font=("Arial", 48, "bold"))
            
        if self.tk_img_issfa:
            self.canvas_menu.create_image(self.issfa_pos_x, 200, image=self.tk_img_issfa)
        else:
            self.canvas_menu.create_rectangle(550, 50, 950, 450, fill="#D32F2F", outline="white", width=3)
            self.canvas_menu.create_text(750, 250, text="ISSFA", fill="white", font=("Arial", 48, "bold"))

        self.btn_iess = tk.Button(self.canvas_menu, text="IESS", font=("Arial", 14), width=15,
                                  command=lambda: self.seleccionar_institucion("IESS"))
        self.btn_issfa = tk.Button(self.canvas_menu, text="ISSFA", font=("Arial", 14), width=15,
                                   command=lambda: self.seleccionar_institucion("ISSFA"))

        self.canvas_menu.create_window(self.iess_pos_x, 450, window=self.btn_iess)
        self.canvas_menu.create_window(self.issfa_pos_x, 450, window=self.btn_issfa)

    def seleccionar_institucion(self, institucion):
        self.institucion_var.set(institucion)
        self.menu_frame.pack_forget()
        self.mostrar_interfaz_principal()

    def mostrar_interfaz_principal(self):
        self.main_frame.pack(fill="both", expand=True)
        self.crear_interfaz_principal()
        self.actualizar_etiquetas()

    def crear_interfaz_principal(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        top = tk.Frame(self.main_frame)
        top.pack(fill="x", padx=10, pady=5)

        tk.Label(top, text="Tipo de documento:").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(top, text="AMB", variable=self.tipo_var, value="AMB", command=self.actualizar_etiquetas).grid(row=0, column=1)
        tk.Radiobutton(top, text="HD", variable=self.tipo_var, value="HD", command=self.actualizar_etiquetas).grid(row=0, column=2)
        tk.Radiobutton(top, text="UNIDO", variable=self.tipo_var, value="UNIDO", command=self.actualizar_etiquetas).grid(row=0, column=3)

        btn_regresar = tk.Button(self.main_frame, text="🔙 Regresar al menú", command=self.regresar_al_menu)
        btn_regresar.pack(side="bottom", anchor="w", padx=10, pady=10)

        tk.Label(top, text="Ruta:").grid(row=1, column=0, sticky="w")
        self.ruta_entry = tk.Entry(top, width=60)
        self.ruta_entry.grid(row=1, column=1, columnspan=3, padx=5)
        tk.Button(top, text="Seleccionar", command=self.seleccionar_ruta).grid(row=1, column=4, padx=5)

        medio = tk.Frame(self.main_frame)
        medio.pack(fill="both", expand=True)

        self.izquierda = tk.Frame(medio)
        self.izquierda.pack(side="left", fill="y", padx=10, pady=5)

        self.panel_imagen = tk.Frame(medio, bg="white", relief="solid", bd=1)
        self.panel_imagen.pack(side="right", expand=True, fill="both", padx=10, pady=5)
        
        self.canvas_img = tk.Canvas(self.panel_imagen, bg="white", highlightthickness=0)
        self.canvas_img.pack(fill="both", expand=True)
        
        self.label_imagen = tk.Label(self.canvas_img, bg="white")
        self.label_imagen.place(relx=0.5, rely=0.5, anchor="center")

        self.botones_etiqueta = []
        self.frame_etiquetas = tk.Frame(self.izquierda)
        self.frame_etiquetas.pack()

        self.frame_funciones = tk.Frame(self.izquierda)
        self.frame_funciones.pack(pady=10)

        self.crear_botones_funciones()

        # Barra de progreso inferior
        info_frame = tk.Frame(self.main_frame)
        info_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        self.info_label = tk.Label(info_frame, text="", font=("Arial", 9))
        self.info_label.pack(side="left", padx=5)

        self.progress_bar = ttk.Progressbar(info_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side="left", padx=10, expand=True, fill="x")

        self.progreso_texto = tk.Label(info_frame, text="", font=("Arial", 9, "bold"), fg="blue")
        self.progreso_texto.pack(side="right", padx=5)

    def actualizar_etiquetas(self):
        for b in self.botones_etiqueta:
            b.destroy()
        self.botones_etiqueta.clear()

        if hasattr(self, "canvas_hoja_blanca") and self.canvas_hoja_blanca.winfo_exists():
            self.canvas_hoja_blanca.destroy()

        etiquetas = ETIQUETAS.get(self.institucion_var.get(), {}).get(self.tipo_var.get(), [])
        etiquetas = [et for et in etiquetas if et.upper() != "HOJA BLANCA"]

        for et in etiquetas:
            b = tk.Button(self.frame_etiquetas, text=et, width=35, anchor="w", command=lambda e=et: self.etiquetar_pagina(e))
            b.pack(pady=1)
            self.botones_etiqueta.append(b)

        self.root.after(50, self.posicionar_hoja_blanca)

    def posicionar_hoja_blanca(self):
        if hasattr(self, "canvas_hoja_blanca") and self.canvas_hoja_blanca.winfo_exists():
            self.canvas_hoja_blanca.destroy()

        self.canvas_hoja_blanca = tk.Canvas(
            self.main_frame,
            width=40,
            height=190,
            bg=self.root.cget("bg"),
            highlightthickness=1,
            highlightbackground="black"
        )

        x = self.frame_etiquetas.winfo_rootx() - self.main_frame.winfo_rootx() + self.frame_etiquetas.winfo_width() + 10
        y = self.frame_etiquetas.winfo_rooty() - self.main_frame.winfo_rooty()

        self.canvas_hoja_blanca.place(x=x, y=y)

        self.canvas_hoja_blanca.create_text(
            20, 105,
            text="HOJA BLANCA",
            angle=90,
            font=("Arial", 10, "bold"),
            fill="black"
        )

        self.canvas_hoja_blanca.bind("<Button-1>", lambda e: self.etiquetar_pagina("HOJA BLANCA"))

    def crear_botones_funciones(self):
        tk.Button(self.frame_funciones, text="⟲ Girar Izq", command=lambda: self.rotar_pagina(-90)).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="Girar Der ⟳", command=lambda: self.rotar_pagina(90)).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="❌ Eliminar página", fg="white", bg="red", command=self.previsualizar_eliminar_paginas).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="⏮ Página anterior", command=self.pagina_anterior).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="Página siguiente ⏭", command=self.pagina_siguiente).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="⏭ Saltar página", command=self.saltar_pagina).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="📄 Mover Página", command=self.previsualizar_mover_paginas).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="📂 Revisar PDF anterior", fg="white", bg="#2196F3", command=self.revisar_pdf_anterior).pack(fill="x", pady=1)
        tk.Button(self.frame_funciones, text="⛔ Omitir PDF", fg="white", bg="gray", command=self.omitir_pdf).pack(fill="x", pady=5)

    def seleccionar_ruta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_entry.delete(0, tk.END)
            self.ruta_entry.insert(0, ruta)
            self.obtener_pdfs(ruta)

    def obtener_pdfs(self, base):
        self.pdfs.clear()
        pdfs_encontrados = []
        
        for raiz, dirs, archivos in os.walk(base):
            dirs.sort(key=natural_sort_key)
            
            for archivo in archivos:
                if archivo.lower().endswith(".pdf"):
                    ruta_pdf = os.path.join(raiz, archivo)
                    nombre_base = os.path.splitext(archivo)[0]
                    carpeta_procesada = os.path.join(raiz, nombre_base)
                    
                    if not os.path.exists(carpeta_procesada):
                        pdfs_encontrados.append(ruta_pdf)
        
        pdfs_encontrados.sort(key=natural_sort_key)
        self.pdfs = pdfs_encontrados
        self.total_pdfs = len(self.pdfs)
        
        self.pdf_index = -1
        if self.pdfs:
            self.cargar_siguiente_pdf()
        else:
            messagebox.showinfo("Info", "No se encontraron PDFs para procesar.")

    def cargar_siguiente_pdf(self):
        self.pdf_index += 1
        if self.pdf_index >= len(self.pdfs):
            messagebox.showinfo("Listo", "Todos los archivos han sido procesados.")
            self.progress_bar["value"] = 100
            self.progreso_texto.config(text="100%")
            return
            
        self.path_pdf = self.pdfs[self.pdf_index]
        self.actual_pdf = self.pdf_index + 1
        
        try:
            if self.doc and not self.doc.is_closed:
                self.doc.close()
                
            self.doc = fitz.open(self.path_pdf)
            self.page_index = 0
            self.page_etiquetas = {}
            self.deleted_pages = set()
            
            # Guardar la rotación original de cada página
            self.rotacion_actual = {}
            for i in range(len(self.doc)):
                self.rotacion_actual[i] = self.doc[i].rotation
                
            self.orden_paginas = list(range(len(self.doc)))
            self.mostrar_pagina()
            self.actualizar_progreso()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el PDF: {str(e)}")
            self.cargar_siguiente_pdf()

    def actualizar_progreso(self):
        if self.total_pdfs > 0 and self.doc:
            porcentaje = (self.actual_pdf / self.total_pdfs) * 100
            self.progress_bar["value"] = porcentaje
            
            nombre_archivo = os.path.basename(self.path_pdf)
            if len(nombre_archivo) > 30:
                nombre_archivo = nombre_archivo[:27] + "..."
            
            total_paginas = len(self.doc)
            carpeta = os.path.basename(os.path.dirname(self.path_pdf))
            
            self.info_label.config(text=f"📁 {carpeta} | 📄 {nombre_archivo} | Página {self.page_index + 1} de {total_paginas}")
            self.progreso_texto.config(text=f"{self.actual_pdf}/{self.total_pdfs}")

    def mostrar_pagina(self):
        if not hasattr(self, "doc") or self.doc.is_closed:
            self.doc = fitz.open(self.path_pdf)
    
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
            
        real_index = self.orden_paginas[self.page_index]
        
        # Obtener la rotación que tenemos registrada
        rot = self.rotacion_actual.get(real_index, 0)
        
        page = self.doc[real_index]
        
        # Guardar rotación original
        rot_original = page.rotation
        
        # Temporalmente poner a 0 para aplicar nuestra rotación
        page.set_rotation(0)
        mat = fitz.Matrix(1, 1).prerotate(rot)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # Restaurar rotación original
        page.set_rotation(rot_original)
        
        # Redimensionar
        ancho_panel = self.panel_imagen.winfo_width()
        alto_panel = self.panel_imagen.winfo_height()
        
        if ancho_panel > 10 and alto_panel > 10:
            ancho_img, alto_img = img.size
            relacion = min(ancho_panel / ancho_img, alto_panel / alto_img)
            nuevo_ancho = int(ancho_img * relacion * 0.95)
            nuevo_alto = int(alto_img * relacion * 0.95)
            img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        else:
            img = img.resize((int(pix.width * 0.7), int(pix.height * 0.7)))
        
        self.tk_img = ImageTk.PhotoImage(img)
        self.label_imagen.config(image=self.tk_img)
        self.actualizar_progreso()

    def etiquetar_pagina(self, etiqueta):
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
        real_index = self.orden_paginas[self.page_index]
        self.page_etiquetas[real_index] = etiqueta
        self.pagina_siguiente()

    def eliminar_pagina(self):
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
        real_index = self.orden_paginas[self.page_index]
        self.deleted_pages.add(real_index)
        self.pagina_siguiente()

    def saltar_pagina(self):
        self.pagina_siguiente()

    def rotar_pagina(self, angulo):
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return

        real_index = self.orden_paginas[self.page_index]

        self.rotacion_actual[real_index] = (
            self.rotacion_actual.get(real_index, 0) + angulo
        ) % 360

        self.mostrar_pagina()

    def pagina_siguiente(self):
        if self.page_index < len(self.orden_paginas) - 1:
            self.page_index += 1
            self.mostrar_pagina()
        else:
            self.guardar_etiquetas()
            self.cargar_siguiente_pdf()

    def pagina_anterior(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.mostrar_pagina()

    def omitir_pdf(self):
        if self.doc and not self.doc.is_closed:
            self.doc.close()
        self.cargar_siguiente_pdf()

    def revisar_pdf_anterior(self):
        if self.pdf_index <= 0:
            messagebox.showinfo("Info", "No hay PDF anterior para revisar.")
            return
        
        pdf_anterior = self.pdfs[self.pdf_index - 1]
        ruta_carpeta = os.path.dirname(pdf_anterior)
        
        try:
            if sys.platform == 'win32':
                os.startfile(ruta_carpeta)
            elif sys.platform == 'darwin':
                subprocess.run(['open', ruta_carpeta])
            else:
                subprocess.run(['xdg-open', ruta_carpeta])
                
            messagebox.showinfo(
                "Éxito", 
                f"Carpeta abierta para revisión.\n\n"
                f"📁 {os.path.basename(ruta_carpeta)}\n"
                f"📄 {os.path.basename(pdf_anterior)}\n\n"
                f"Recuerde que está procesando: {os.path.basename(self.path_pdf)}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta.\n\n{ruta_carpeta}")

    def previsualizar_mover_paginas(self):
        mover_win = tk.Toplevel(self.root)
        mover_win.title("Reordenar páginas")
        mover_win.geometry("1200x700")

        main_frame = tk.Frame(mover_win)
        main_frame.pack(fill="both", expand=True, side="left")

        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", update_scrollregion)

        btn_frame = tk.Frame(mover_win, width=150)
        btn_frame.pack(side="right", fill="y", padx=10, pady=10)

        if not hasattr(self, "doc") or self.doc.is_closed:
            self.doc = fitz.open(self.path_pdf)

        self.selected_pages = set()
        self.thumbnails_widgets = []
        self.drag_data = {"item": None, "x": 0, "y": 0, "ghost": None}

        def toggle_selection(page_num, container):
            if page_num in self.selected_pages:
                self.selected_pages.remove(page_num)
                container.config(highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            else:
                self.selected_pages.add(page_num)
                container.config(highlightbackground="red", highlightcolor="red", highlightthickness=3)

        def on_thumbnail_click(event, page_num, container):
            ctrl_pressed = (event.state & 0x4) == 0x4
            
            if ctrl_pressed:
                toggle_selection(page_num, container)
            else:
                for p, c in self.thumbnails_widgets:
                    if p in self.selected_pages:
                        c.config(highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
                self.selected_pages.clear()
                toggle_selection(page_num, container)

        def start_drag(event, page_num, container):
            self.drag_data["item"] = (page_num, container)
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root

        def during_drag(event):
            if not self.drag_data["item"]:
                return
                
            if not self.drag_data.get("ghost"):
                page_num, container = self.drag_data["item"]
                ghost = tk.Toplevel(mover_win)
                ghost.overrideredirect(True)
                ghost.geometry(f"+{event.x_root}+{event.y_root}")
                
                img = container.tkimg
                label = tk.Label(ghost, image=img, bd=2, relief="solid", bg="white")
                label.pack()
                
                self.drag_data["ghost"] = ghost
                self.drag_data["offset_x"] = event.x
                self.drag_data["offset_y"] = event.y
            
            if self.drag_data["ghost"]:
                ghost = self.drag_data["ghost"]
                ghost.geometry(f"+{event.x_root - self.drag_data['offset_x']}+{event.y_root - self.drag_data['offset_y']}")

        def end_drag(event):
            if not self.drag_data["item"]:
                return
                
            page_num, container = self.drag_data["item"]
            x, y = event.x_root, event.y_root
            
            closest_idx = None
            min_dist = float('inf')
            
            for idx, (p_num, cont) in enumerate(self.thumbnails_widgets):
                cont_x = cont.winfo_rootx() + cont.winfo_width() // 2
                cont_y = cont.winfo_rooty() + cont.winfo_height() // 2
                dist = (cont_x - x)**2 + (cont_y - y)**2
                
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = idx
            
            if closest_idx is not None:
                current_idx = self.orden_paginas.index(page_num)
                if closest_idx != current_idx:
                    self.orden_paginas.pop(current_idx)
                    self.orden_paginas.insert(closest_idx, page_num)
                    refresh_thumbnails()

            if self.drag_data["ghost"]:
                self.drag_data["ghost"].destroy()
            self.drag_data["ghost"] = None
            self.drag_data["item"] = None

        def refresh_thumbnails():
            for child in frame.winfo_children():
                child.destroy()
            
            self.thumbnails_widgets = []
            temp_selected = self.selected_pages.copy()
            self.selected_pages.clear()

            orden_temp = self.orden_paginas.copy()

            for idx, page_num in enumerate(orden_temp):
                page = self.doc[page_num]
                try:
                    rot = self.rotacion_actual.get(page_num, 0)
                    
                    rot_original = page.rotation
                    page.set_rotation(0)
                    mat = fitz.Matrix(1, 1).prerotate(rot)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.open(io.BytesIO(pix.tobytes("png"))).resize((120, 170), Image.Resampling.LANCZOS)
                    page.set_rotation(rot_original)
                except Exception as e:
                    print(f"Error miniatura página {page_num}: {e}")
                    continue

                tkimg = ImageTk.PhotoImage(img)
                cont = tk.Frame(frame, bd=2, relief="solid", 
                                highlightbackground="gray", 
                                highlightcolor="gray", 
                                highlightthickness=1)
                cont.grid(row=idx // 5, column=idx % 5, padx=5, pady=5)
                cont.tkimg = tkimg

                lbl = tk.Label(cont, image=tkimg)
                lbl.pack()
                lbl_text = tk.Label(cont, text=f"Pág {page_num + 1}")
                lbl_text.pack()

                def bind_events(widget, p_num, container):
                    widget.bind("<Button-1>", lambda e: on_thumbnail_click(e, p_num, container))
                    widget.bind("<B1-Motion>", during_drag)
                    widget.bind("<ButtonRelease-1>", end_drag)
                    widget.bind("<ButtonPress-1>", lambda e: start_drag(e, p_num, container))

                for widget in [cont, lbl, lbl_text]:
                    bind_events(widget, page_num, cont)

                if page_num in temp_selected:
                    cont.config(highlightbackground="red", highlightcolor="red", highlightthickness=3)
                    self.selected_pages.add(page_num)

                self.thumbnails_widgets.append((page_num, cont))

        def eliminar_paginas_seleccionadas():
            if not self.selected_pages:
                messagebox.showwarning("Advertencia", "No hay páginas seleccionadas para eliminar. Usa Ctrl + click para seleccionar.")
                return
            self.deleted_pages.update(self.selected_pages)
            self.orden_paginas = [p for p in self.orden_paginas if p not in self.deleted_pages]
            self.selected_pages.clear()
            refresh_thumbnails()

        def confirmar_orden():
            new_doc = fitz.open()

            for old_idx in self.orden_paginas:
                # Insertar la página copiando la rotación original
                new_doc.insert_pdf(self.doc, from_page=old_idx, to_page=old_idx)
                
                # Aplicar la rotación que tenemos registrada
                rot = self.rotacion_actual.get(old_idx, 0)
                if rot != 0:
                    last_page = new_doc[-1]
                    last_page.set_rotation(rot)

            if hasattr(self, "doc") and not self.doc.is_closed:
                self.doc.close()

            self.doc = new_doc

            old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(self.orden_paginas)}

            self.orden_paginas = list(range(len(self.doc)))
            self.deleted_pages.clear()
            self.page_index = 0

            self.page_etiquetas = {
                new_idx: self.page_etiquetas[old_idx]
                for old_idx, new_idx in old_to_new.items()
                if old_idx in self.page_etiquetas
            }

            self.rotacion_actual = {
                new_idx: self.rotacion_actual[old_idx]
                for old_idx, new_idx in old_to_new.items()
                if old_idx in self.rotacion_actual
            }

            mover_win.destroy()
            self.mostrar_pagina()

        btn_confirmar = tk.Button(btn_frame, text="✅ Confirmar orden", command=confirmar_orden, width=20)
        btn_confirmar.pack(fill="x", pady=5)

        btn_cancelar = tk.Button(btn_frame, text="✖ Cancelar", command=mover_win.destroy, width=20)
        btn_cancelar.pack(fill="x", pady=5)

        refresh_thumbnails()

    def previsualizar_eliminar_paginas(self):
        eliminar_win = tk.Toplevel(self.root)
        eliminar_win.title("Eliminar páginas")
        eliminar_win.geometry("1200x700")

        main_frame = tk.Frame(eliminar_win)
        main_frame.pack(fill="both", expand=True, side="left")

        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", update_scrollregion)

        btn_frame = tk.Frame(eliminar_win, width=150)
        btn_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        if not hasattr(self, "doc") or self.doc.is_closed:
            self.doc = fitz.open(self.path_pdf)

        self.selected_pages = set()
        self.thumbnails_widgets = []

        def toggle_selection(page_num, container):
            if page_num in self.selected_pages:
                self.selected_pages.remove(page_num)
                container.config(highlightbackground="gray", highlightthickness=1)
            else:
                self.selected_pages.add(page_num)
                container.config(highlightbackground="red", highlightthickness=3)

        def on_click(event, page_num, container):
            ctrl = (event.state & 0x4) == 0x4
            if not ctrl:
                for p, c in self.thumbnails_widgets:
                    c.config(highlightbackground="gray", highlightthickness=1)
                self.selected_pages.clear()
            toggle_selection(page_num, container)

        def refresh_thumbnails():
            for child in frame.winfo_children():
                child.destroy()

            self.thumbnails_widgets = []
            temp_selected = self.selected_pages.copy()
            self.selected_pages.clear()

            orden_temp = [i for i in range(len(self.doc)) if i not in self.deleted_pages]

            for idx, page_num in enumerate(orden_temp):
                page = self.doc[page_num]
                try:
                    rot = self.rotacion_actual.get(page_num, 0)
                    
                    rot_original = page.rotation
                    page.set_rotation(0)
                    mat = fitz.Matrix(1, 1).prerotate(rot)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.open(io.BytesIO(pix.tobytes("png"))).resize((120, 170), Image.Resampling.LANCZOS)
                    page.set_rotation(rot_original)
                except Exception as e:
                    print("Error miniatura:", e)
                    continue

                tkimg = ImageTk.PhotoImage(img)
                cont = tk.Frame(frame, bd=2, relief="solid", highlightbackground="gray", highlightthickness=1)
                cont.grid(row=idx // 5, column=idx % 5, padx=5, pady=5)
                cont.tkimg = tkimg

                lbl = tk.Label(cont, image=tkimg)
                lbl.pack()
                tk.Label(cont, text=f"Pág {page_num + 1}").pack()

                for w in [cont, lbl]:
                    w.bind("<Button-1>", lambda e, p=page_num, c=cont: on_click(e, p, c))

                if page_num in temp_selected:
                    cont.config(highlightbackground="red", highlightthickness=3)
                    self.selected_pages.add(page_num)

                self.thumbnails_widgets.append((page_num, cont))

        def eliminar_paginas_seleccionadas():
            if not self.selected_pages:
                messagebox.showwarning("Advertencia", "Selecciona páginas con Ctrl + click.")
                return
            self.deleted_pages.update(self.selected_pages)
            self.orden_paginas = [p for p in self.orden_paginas if p not in self.deleted_pages]
            self.selected_pages.clear()
            refresh_thumbnails()

        def confirmar_eliminacion():
            new_doc = fitz.open()
            
            nuevas_paginas = [i for i in range(len(self.doc)) if i not in self.deleted_pages]
            
            for old_idx in nuevas_paginas:
                new_doc.insert_pdf(self.doc, from_page=old_idx, to_page=old_idx)
                rot = self.rotacion_actual.get(old_idx, 0)
                if rot != 0:
                    last_page = new_doc[-1]
                    last_page.set_rotation(rot)
            
            if self.doc and not self.doc.is_closed:
                self.doc.close()
            
            self.doc = new_doc
            
            old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(nuevas_paginas)}
            
            self.orden_paginas = list(range(len(self.doc)))
            self.deleted_pages.clear()
            self.page_index = 0
            
            self.page_etiquetas = {
                new_idx: self.page_etiquetas[old_idx]
                for old_idx, new_idx in old_to_new.items()
                if old_idx in self.page_etiquetas
            }
            
            self.rotacion_actual = {
                new_idx: self.rotacion_actual[old_idx]
                for old_idx, new_idx in old_to_new.items()
                if old_idx in self.rotacion_actual
            }

            eliminar_win.destroy()
            self.mostrar_pagina()

        tk.Button(btn_frame, text="✅ Confirmar eliminación", command=confirmar_eliminacion, width=20).pack(fill="x", pady=5)
        tk.Button(btn_frame, text="❌ Eliminar seleccionadas", command=eliminar_paginas_seleccionadas, width=20, bg="red", fg="white").pack(fill="x", pady=5)
        tk.Button(btn_frame, text="✖ Cancelar", command=eliminar_win.destroy, width=20).pack(fill="x", pady=5)

        refresh_thumbnails()

    def guardar_etiquetas(self):
        base_dir = os.path.dirname(self.path_pdf)
        nombre_carpeta = os.path.basename(base_dir)
        agrupadas = {}
        for i in self.orden_paginas:
            if i in self.deleted_pages:
                continue
            etiqueta = self.page_etiquetas.get(i)
            if not etiqueta:
                for j in range(i - 1, -1, -1):
                    if j in self.page_etiquetas:
                        etiqueta = self.page_etiquetas[j]
                        break
            if not etiqueta:
                etiqueta = "SIN_ETIQUETA"
            agrupadas.setdefault(etiqueta, []).append(i)

        if self.tipo_var.get() == "AMB" and self.institucion_var.get() == "IESS":
            etiquetas_ordenadas = list(agrupadas.keys())
            etiquetas_ordenadas = [et for et in etiquetas_ordenadas if et != "HOJA BLANCA"]

            primera_etiqueta = etiquetas_ordenadas[0] if etiquetas_ordenadas else None

            if primera_etiqueta and "." in primera_etiqueta:
                partes = primera_etiqueta.split(".", 1)
                if partes[0].strip().isdigit():
                    numero_inicio = int(partes[0].strip())
                else:
                    numero_inicio = 1
            else:
                numero_inicio = 1

            etiquetas_numeradas = {}
            for idx, et in enumerate(etiquetas_ordenadas, start=numero_inicio):
                texto_sin_num = et.split(".", 1)[1].strip() if "." in et else et
                etiquetas_numeradas[f"{idx}. {texto_sin_num}"] = agrupadas[et]

            for etiqueta, indices in etiquetas_numeradas.items():
                nuevo_doc = fitz.open()
                for i in indices:
                    nuevo_doc.insert_pdf(self.doc, from_page=i, to_page=i)
                    rot = self.rotacion_actual.get(i, 0)
                    if rot != 0:
                        last_page = nuevo_doc[-1]
                        last_page.set_rotation(rot)
                nuevo_doc.save(os.path.join(base_dir, f"{etiqueta}.pdf"))
                nuevo_doc.close()

            if "HOJA BLANCA" in agrupadas:
                nuevo_doc = fitz.open()
                for i in agrupadas["HOJA BLANCA"]:
                    nuevo_doc.insert_pdf(self.doc, from_page=i, to_page=i)
                    rot = self.rotacion_actual.get(i, 0)
                    if rot != 0:
                        last_page = nuevo_doc[-1]
                        last_page.set_rotation(rot)
                nuevo_doc.save(os.path.join(base_dir, "Hoja Blanca.pdf"))
                nuevo_doc.close()

        elif self.tipo_var.get() == "AMB" and self.institucion_var.get() == "ISSFA":
            for etiqueta, indices in agrupadas.items():
                nuevo_doc = fitz.open()
                for i in indices:
                    nuevo_doc.insert_pdf(self.doc, from_page=i, to_page=i)
                    rot = self.rotacion_actual.get(i, 0)
                    if rot != 0:
                        last_page = nuevo_doc[-1]
                        last_page.set_rotation(rot)
                nombre_archivo = f"{nombre_carpeta}-{etiqueta}.pdf"
                nuevo_doc.save(os.path.join(base_dir, nombre_archivo))
                nuevo_doc.close()

        elif self.tipo_var.get() == "UNIDO":
            for etiqueta, indices in agrupadas.items():
                if etiqueta == "HOJA BLANCA":
                    continue
                nuevo_doc = fitz.open()
                for i in indices:
                    nuevo_doc.insert_pdf(self.doc, from_page=i, to_page=i)
                    rot = self.rotacion_actual.get(i, 0)
                    if rot != 0:
                        last_page = nuevo_doc[-1]
                        last_page.set_rotation(rot)
                nuevo_doc.save(os.path.join(base_dir, f"{etiqueta}.pdf"))
                nuevo_doc.close()

            if "HOJA BLANCA" in agrupadas:
                nuevo_doc = fitz.open()
                for i in agrupadas["HOJA BLANCA"]:
                    nuevo_doc.insert_pdf(self.doc, from_page=i, to_page=i)
                    rot = self.rotacion_actual.get(i, 0)
                    if rot != 0:
                        last_page = nuevo_doc[-1]
                        last_page.set_rotation(rot)
                nuevo_doc.save(os.path.join(base_dir, "Hoja Blanca.pdf"))
                nuevo_doc.close()

        else:
            for etiqueta, indices in agrupadas.items():
                nuevo_doc = fitz.open()
                for i in indices:
                    nuevo_doc.insert_pdf(self.doc, from_page=i, to_page=i)
                    rot = self.rotacion_actual.get(i, 0)
                    if rot != 0:
                        last_page = nuevo_doc[-1]
                        last_page.set_rotation(rot)
                nuevo_doc.save(os.path.join(base_dir, f"{etiqueta}.pdf"))
                nuevo_doc.close()

    def regresar_al_menu(self):
        self.main_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFApp(root)
    root.mainloop()
