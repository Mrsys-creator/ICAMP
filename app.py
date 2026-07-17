import sys
import os
import re
import subprocess
import shutil

def obtener_ruta_recurso(nombre_archivo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_archivo)
    return os.path.join(os.path.abspath("."), nombre_archivo)

def obtener_ruta_reportes():
    """Obtiene la ruta de la carpeta de reportes en la raíz de instalación"""
    if getattr(sys, 'frozen', False):
        # Si está empaquetado, usar la carpeta donde está el ejecutable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Si está en desarrollo, usar la carpeta actual
        base_dir = os.path.abspath(".")
    
    carpeta_reportes = os.path.join(base_dir, "Reportes")
    os.makedirs(carpeta_reportes, exist_ok=True)
    return carpeta_reportes

import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import io
from datetime import datetime

# ===== NUEVO: CustomTkinter =====
import customtkinter as ctk

import urllib.request
import json
import threading
import time

# ===== IMPORTAR PARA EL UNIDOR =====
from PyPDF2 import PdfMerger
from pathlib import Path
from collections import defaultdict

# ============================================
# 🚀 SISTEMA DE ACTUALIZACIONES AUTOMÁTICAS
# ============================================

class Actualizador:
    URL_VERSION = "https://raw.githubusercontent.com/Mrsys-creator/ICAMP/main/version.json"
    VERSION_ACTUAL = "1.0.9"
    NOMBRE_APP = "_IC@MP_"
    
    # ===== URL DE DESCARGA POR DEFECTO =====
    URL_DESCARGA_DEFAULT = "https://github.com/Mrsys-creator/ICAMP/releases/download/v{version}/RenombradorPDF.exe"
    
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
            url_descarga = data.get("url_descarga", "")
            mensaje = data.get("mensaje", "Nueva versión disponible")
            
            # ===== SI NO HAY URL, USAR LA DEFAULT =====
            if not url_descarga:
                url_descarga = Actualizador.URL_DESCARGA_DEFAULT.format(version=version_remota)
                print(f"📌 Usando URL por defecto: {url_descarga}")
            
            if Actualizador._es_version_mayor(version_remota, Actualizador.VERSION_ACTUAL):
                respuesta = messagebox.askyesno(
                    f"📦 {Actualizador.NOMBRE_APP} - Actualización disponible",
                    f"🔔 Nueva versión **{version_remota}** disponible.\n\n"
                    f"📌 Cambios:\n{mensaje}\n\n"
                    f"¿Deseas descargar e instalar la actualización ahora?"
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

# ============================================
# 🔗 UNIDOR DE PDFS (NUEVA FUNCIONALIDAD)
# ============================================

class PDFUnidorApp:
    """Aplicación para unir PDFs por carpeta"""
    
    def __init__(self, parent_frame, volver_callback, app_reference=None):
        self.parent_frame = parent_frame
        self.volver_callback = volver_callback
        self.app_reference = app_reference  # Referencia a la app principal
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.output_filename = tk.StringVar(value="13. ANEXOS")
        self.nombres_unicos = []
        self.pdfs_por_carpeta = {}
        self.estructura_completa = {}
        self.estado_progreso = tk.DoubleVar()
        self.ruta_escaneda = ""
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Limpiar frame padre
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=3)
        
        # Título
        titulo = ctk.CTkLabel(
            main_frame, 
            text="🔗 UNIDOR DE PDFs POR CARPETA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1A237E"
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # ===== QUITAR EL BOTÓN REGRESAR DE ARRIBA =====
        
        # Selección de carpeta
        ctk.CTkLabel(main_frame, text="📁 Carpeta principal a escanear:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        folder_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.selected_folder, state='readonly', height=35)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ctk.CTkButton(
            folder_frame, 
            text="📁 Buscar", 
            command=self.select_folder,
            height=35,
            width=100
        ).grid(row=0, column=1)
        
        # Botón escanear
        self.scan_btn = ctk.CTkButton(
            main_frame, 
            text="🔍 Escanear PDFs en todas las subcarpetas",
            command=self.scan_pdfs,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.scan_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Frame para lista
        list_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA", corner_radius=10)
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Scrollable frame para checkboxes
        self.scrollable_frame = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Variables para checkboxes
        self.check_vars = []
        self.checkboxes = []
        
        # Frame información
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.info_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=11))
        self.info_label.pack()
        
        # Botones selección
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ctk.CTkButton(
            btn_frame, 
            text="📋 Seleccionar todos",
            command=self.select_all,
            height=30,
            width=140
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="📋 Deseleccionar todos",
            command=self.deselect_all,
            height=30,
            width=140
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame nombre salida
        output_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        output_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        output_frame.columnconfigure(0, weight=0)
        output_frame.columnconfigure(1, weight=1)
        output_frame.columnconfigure(2, weight=0)
        
        ctk.CTkLabel(output_frame, text="📤 Nombre archivo:").grid(row=0, column=0, padx=(0, 10))
        
        self.output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_filename, height=35)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ctk.CTkLabel(output_frame, text=".pdf").grid(row=0, column=2)
        
        # Botón unir
        self.merge_btn = ctk.CTkButton(
            main_frame, 
            text="🔄 UNIR PDFS EN CADA CARPETA",
            command=self.merge_pdfs,
            state='disabled',
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1A237E",
            hover_color="#0D1555"
        )
        self.merge_btn.grid(row=8, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))
        
        # ===== BARRA DE PROGRESO (ARRIBA DE LOS BOTONES) =====
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.grid(row=9, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=15)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            main_frame, 
            text="Listo para comenzar",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=10, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # ===== BOTONES INFERIORES (ABAJO DE LA BARRA DE PROGRESO) =====
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.grid(row=11, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Botón Regresar al menú (IZQUIERDA)
        btn_regresar_menu = ctk.CTkButton(
            bottom_frame, 
            text="🔙 Regresar al menú",
            fg_color="#78909C", 
            hover_color="#546E7A",
            height=30, 
            width=140,
            command=self.volver_callback
        )
        btn_regresar_menu.pack(side=tk.LEFT, padx=5)
        
        # Botón Reportes (DERECHA)
        self.btn_reportes = ctk.CTkButton(
            bottom_frame, 
            text="📊 Reportes",
            fg_color="#2E7D32", 
            hover_color="#1B5E20",
            height=30, 
            width=120,
            command=self.abrir_reportes,
            state='disabled'
        )
        self.btn_reportes.pack(side=tk.RIGHT, padx=5)
        
    def abrir_reportes(self):
        """Abre la carpeta de reportes"""
        carpeta_reportes = obtener_ruta_reportes()
        try:
            if sys.platform == 'win32':
                os.startfile(carpeta_reportes)
            elif sys.platform == 'darwin':
                subprocess.run(['open', carpeta_reportes])
            else:
                subprocess.run(['xdg-open', carpeta_reportes])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta de reportes:\n\n{str(e)}")
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta principal")
        if folder:
            self.selected_folder.set(folder)
            self.ruta_escaneda = folder
            self.status_label.configure(text=f"Carpeta seleccionada: {folder}")
            self.scan_btn.configure(state='normal')
            self.clear_list()
            
    def scan_pdfs(self):
        if not self.selected_folder.get():
            messagebox.showerror("Error", "Primero selecciona una carpeta")
            return
            
        self.status_label.configure(text="🔍 Escaneando PDFs en todas las subcarpetas...")
        self.scan_btn.configure(state='disabled')
        self.root.update()
        
        threading.Thread(target=self.scan_pdfs_thread, daemon=True).start()
        
    def scan_pdfs_thread(self):
        try:
            self.pdfs_por_carpeta = {}
            self.estructura_completa = {}
            self.nombres_unicos = []
            
            root_path = Path(self.selected_folder.get())
            
            for carpeta in root_path.iterdir():
                if carpeta.is_dir():
                    pdfs_en_carpeta = []
                    for pdf_path in carpeta.rglob("*.pdf"):
                        nombre = pdf_path.name
                        pdfs_en_carpeta.append(str(pdf_path))
                        
                        if nombre not in self.estructura_completa:
                            self.estructura_completa[nombre] = {}
                        self.estructura_completa[nombre][str(carpeta)] = str(pdf_path)
                    
                    if pdfs_en_carpeta:
                        self.pdfs_por_carpeta[str(carpeta)] = pdfs_en_carpeta
            
            self.nombres_unicos = sorted(self.estructura_completa.keys())
            self.root.after(0, self.update_list)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.configure(
                text=f"❌ Error al escanear: {str(e)}"))
            self.root.after(0, lambda: self.scan_btn.configure(state='normal'))
            
    def update_list(self):
        # Limpiar lista anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.check_vars = []
        self.checkboxes = []
        
        if not self.nombres_unicos:
            ctk.CTkLabel(
                self.scrollable_frame, 
                text="No se encontraron PDFs en las subcarpetas",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
            self.status_label.configure(text="No se encontraron PDFs")
            self.merge_btn.configure(state='disabled')
            self.info_label.configure(text="")
            self.scan_btn.configure(state='normal')
            self.btn_reportes.configure(state='normal')
            return
        
        # Crear checkboxes para cada nombre único
        for nombre in self.nombres_unicos:
            var = tk.BooleanVar()
            self.check_vars.append(var)
            
            num_carpetas = len(self.estructura_completa[nombre])
            texto = f"📄 {nombre}  ({num_carpetas} carpetas)"
            
            cb = ctk.CTkCheckBox(
                self.scrollable_frame, 
                text=texto, 
                variable=var,
                font=ctk.CTkFont(size=12)
            )
            cb.pack(anchor=tk.W, pady=3, padx=5)
            self.checkboxes.append(cb)
        
        self.status_label.configure(text=f"✅ Se encontraron {len(self.nombres_unicos)} nombres únicos de PDFs")
        self.merge_btn.configure(state='normal')
        self.scan_btn.configure(state='normal')
        self.btn_reportes.configure(state='normal')
        
        total_carpetas = len(self.pdfs_por_carpeta)
        total_pdfs = sum(len(pdfs) for pdfs in self.pdfs_por_carpeta.values())
        self.info_label.configure(text=f"📊 {len(self.nombres_unicos)} nombres únicos | {total_carpetas} carpetas | {total_pdfs} archivos PDF")
        
    def select_all(self):
        for var in self.check_vars:
            var.set(True)
        self.status_label.configure(text=f"Seleccionados todos los {len(self.check_vars)} nombres")
        
    def deselect_all(self):
        for var in self.check_vars:
            var.set(False)
        self.status_label.configure(text="Todos los nombres deseleccionados")
        
    def get_selected_names(self):
        selected = []
        for i, var in enumerate(self.check_vars):
            if var.get():
                selected.append(self.nombres_unicos[i])
        return selected
        
    def clear_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.nombres_unicos = []
        self.pdfs_por_carpeta = {}
        self.estructura_completa = {}
        self.check_vars = []
        self.checkboxes = []
        self.merge_btn.configure(state='disabled')
        self.info_label.configure(text="")
        self.progress_bar.set(0)
        
    def merge_pdfs(self):
        selected_names = self.get_selected_names()
        
        if not selected_names:
            messagebox.showwarning("Advertencia", "No has seleccionado ningún nombre de PDF")
            return
            
        if len(selected_names) < 2:
            messagebox.showwarning("Advertencia", "Selecciona al menos 2 nombres diferentes para unir")
            return
        
        carpetas_a_procesar = len(self.pdfs_por_carpeta)
        total_archivos = 0
        for nombre in selected_names:
            total_archivos += len(self.estructura_completa[nombre])
        
        if not messagebox.askyesno("Confirmar", 
                                  f"📊 Resumen:\n"
                                  f"- {len(selected_names)} nombres seleccionados\n"
                                  f"- {carpetas_a_procesar} carpetas a procesar\n"
                                  f"- {total_archivos} archivos PDF en total\n\n"
                                  f"En CADA carpeta se unirán los PDFs seleccionados\n"
                                  f"y se guardarán como '{self.output_filename.get()}.pdf'\n"
                                  f"en su respectiva carpeta.\n\n"
                                  f"¿Continuar?"):
            return
            
        self.merge_btn.configure(state='disabled')
        self.status_label.configure(text="🔄 Uniendo PDFs en cada carpeta...")
        threading.Thread(target=self.merge_pdfs_thread, args=(selected_names,), daemon=True).start()
        
    def merge_pdfs_thread(self, selected_names):
        try:
            output_name = self.output_filename.get().strip()
            if not output_name:
                output_name = "13. ANEXOS"
            
            carpetas_procesadas = 0
            total_carpetas = len(self.pdfs_por_carpeta)
            errores = []
            carpetas_sin_suficientes = 0
            carpetas_exitosas = []
            
            for carpeta, pdfs in self.pdfs_por_carpeta.items():
                carpeta_path = Path(carpeta)
                
                pdfs_a_unir = []
                for pdf_path in pdfs:
                    nombre_pdf = Path(pdf_path).name
                    if nombre_pdf in selected_names:
                        pdfs_a_unir.append(pdf_path)
                
                if len(pdfs_a_unir) >= 2:
                    output_path = carpeta_path / f"{output_name}.pdf"
                    contador = 1
                    while output_path.exists():
                        output_path = carpeta_path / f"{output_name} ({contador}).pdf"
                        contador += 1
                    
                    merger = PdfMerger()
                    try:
                        for pdf_path in pdfs_a_unir:
                            merger.append(pdf_path)
                        
                        merger.write(str(output_path))
                        merger.close()
                        
                        carpetas_procesadas += 1
                        carpetas_exitosas.append(f"{carpeta_path.name} → {output_path.name}")
                        
                        progreso = (carpetas_procesadas / total_carpetas) * 100
                        self.root.after(0, lambda p=progreso: self.progress_bar.set(p/100))
                        self.root.after(0, lambda c=carpeta_path.name, t=len(pdfs_a_unir): 
                                       self.status_label.configure(
                                           text=f"✅ Unido en {c}: {t} PDFs → {output_path.name}"))
                        
                    except Exception as e:
                        errores.append(f"{carpeta_path.name}: {str(e)}")
                else:
                    carpetas_sin_suficientes += 1
                    self.root.after(0, lambda c=carpeta_path.name, t=len(pdfs_a_unir): 
                                   self.status_label.configure(
                                       text=f"⏭️ {c}: solo {t} PDFs seleccionados (mínimo 2)"))
            
            self.root.after(0, lambda: self.progress_bar.set(1))
            
            # Generar reporte
            self.generar_reporte_unidor(selected_names, carpetas_exitosas, carpetas_sin_suficientes, errores, output_name)
            
            mensaje_final = f"✅ Proceso completado:\n"
            mensaje_final += f"- {carpetas_procesadas} carpetas procesadas exitosamente\n"
            mensaje_final += f"- {len(selected_names)} nombres de PDFs unidos por carpeta\n"
            
            if carpetas_sin_suficientes > 0:
                mensaje_final += f"\n⏭️ {carpetas_sin_suficientes} carpetas sin suficientes PDFs (mínimo 2)"
            
            if errores:
                mensaje_final += f"\n\n❌ {len(errores)} carpetas con errores"
                if len(errores) <= 3:
                    mensaje_final += "\n" + "\n".join(errores)
                else:
                    mensaje_final += f"\n(Error en {len(errores)} carpetas)"
            
            self.root.after(0, lambda: self.status_label.configure(
                text=f"✅ Completado: {carpetas_procesadas} carpetas procesadas"))
            self.root.after(0, lambda: self.merge_btn.configure(state='normal'))
            self.root.after(0, lambda: self.btn_reportes.configure(state='normal'))
            
            # Limpiar interfaz después de completar
            self.root.after(500, self.limpiar_interfaz_unidor)
            
            if errores:
                self.root.after(0, lambda: messagebox.showwarning("Advertencia", mensaje_final))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Éxito", mensaje_final))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error general: {str(e)}"))
            self.root.after(0, lambda: self.status_label.configure(text="❌ Error al unir PDFs"))
            self.root.after(0, lambda: self.merge_btn.configure(state='normal'))
    
    def generar_reporte_unidor(self, selected_names, carpetas_exitosas, carpetas_sin_suficientes, errores, output_name):
        """Genera el reporte para el unidor de PDFs"""
        try:
            fecha_hora = datetime.now()
            fecha_str = fecha_hora.strftime("%Y-%m-%d_%H-%M-%S")
            
            carpeta_reportes = obtener_ruta_reportes()
            nombre_reporte = f"Reporte_UNIDOR_{fecha_str}.txt"
            ruta_reporte = os.path.join(carpeta_reportes, nombre_reporte)
            
            with open(ruta_reporte, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("REPORTE DE UNIÓN DE PDFs\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Fecha: {fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Carpeta escaneada: {self.ruta_escaneda}\n")
                f.write(f"Nombre de salida: {output_name}.pdf\n\n")
                f.write("-" * 80 + "\n")
                f.write("RESUMEN\n")
                f.write("-" * 80 + "\n")
                f.write(f"Nombres seleccionados: {', '.join(selected_names)}\n")
                f.write(f"Carpetas procesadas exitosamente: {len(carpetas_exitosas)}\n")
                f.write(f"Carpetas sin suficientes PDFs: {carpetas_sin_suficientes}\n")
                f.write(f"Carpetas con errores: {len(errores)}\n\n")
                
                if carpetas_exitosas:
                    f.write("-" * 80 + "\n")
                    f.write("CARPETAS PROCESADAS EXITOSAMENTE\n")
                    f.write("-" * 80 + "\n")
                    for item in carpetas_exitosas:
                        f.write(f"  ✅ {item}\n")
                    f.write("\n")
                
                if errores:
                    f.write("-" * 80 + "\n")
                    f.write("ERRORES\n")
                    f.write("-" * 80 + "\n")
                    for error in errores:
                        f.write(f"  ❌ {error}\n")
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("FIN DEL REPORTE\n")
                f.write("=" * 80 + "\n")
            
            # Habilitar botón de reportes
            self.root.after(0, lambda: self.btn_reportes.configure(state='normal'))
            
        except Exception as e:
            print(f"Error al generar reporte: {e}")
    
    def limpiar_interfaz_unidor(self):
        """Limpia la interfaz del unidor después de completar"""
        self.selected_folder.set("")
        self.folder_entry.configure(state='normal')
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.configure(state='readonly')
        self.clear_list()
        self.progress_bar.set(0)
        self.status_label.configure(text="Listo para comenzar")
        self.scan_btn.configure(state='normal')
        self.merge_btn.configure(state='disabled')
        self.btn_reportes.configure(state='normal')
    
    @property
    def root(self):
        """Obtener el root desde el parent_frame"""
        return self.parent_frame.winfo_toplevel()

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
        
        # ===== CONFIGURACIÓN DE CustomTkinter =====
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.root.title("_IC@MP_")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)
        self.root.resizable(True, True)

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
        self.ruta_escaneda = ""  # Guardar ruta para reportes

        self.doc = None
        self.path_pdf = None

        # Frames principales
        self.menu_frame = tk.Frame(self.root, width=1000, height=600)
        self.menu_frame.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.root, width=1000, height=600)

        self.crear_menu_inicio()
    
        verificar_actualizacion_al_inicio()

    def abrir_reportes(self):
        """Abre la carpeta de reportes"""
        carpeta_reportes = obtener_ruta_reportes()
        try:
            if sys.platform == 'win32':
                os.startfile(carpeta_reportes)
            elif sys.platform == 'darwin':
                subprocess.run(['open', carpeta_reportes])
            else:
                subprocess.run(['xdg-open', carpeta_reportes])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta de reportes:\n\n{str(e)}")

    def verificar_documento_abierto(self):
        """Verifica que el documento esté abierto y sea accesible"""
        try:
            if not hasattr(self, "doc") or self.doc is None:
                return False
            if hasattr(self.doc, 'is_closed') and self.doc.is_closed:
                return False
            return True
        except:
            return False

    def cerrar_documento_seguro(self):
        """Cierra el documento de forma segura sin generar errores"""
        if hasattr(self, "doc"):
            try:
                if self.doc is not None:
                    try:
                        if hasattr(self.doc, 'is_closed') and not self.doc.is_closed:
                            self.doc.close()
                    except (ValueError, AttributeError, RuntimeError):
                        pass
            except Exception:
                pass
            self.doc = None

    def limpiar_interfaz_completa(self):
        """Limpia toda la interfaz y la deja como nueva"""
        # Cerrar documento
        self.cerrar_documento_seguro()
        
        # Limpiar variables
        self.pdfs = []
        self.pdf_index = -1
        self.page_index = 0
        self.page_etiquetas = {}
        self.deleted_pages = set()
        self.rotacion_actual = {}
        self.orden_paginas = []
        self.total_pdfs = 0
        self.actual_pdf = 0
        self.path_pdf = None
        
        # Limpiar campo de ruta
        if hasattr(self, 'ruta_entry'):
            self.ruta_entry.delete(0, tk.END)
        
        # Resetear barra de progreso
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set(0)
        if hasattr(self, 'progreso_texto'):
            self.progreso_texto.configure(text="")
        if hasattr(self, 'info_label'):
            self.info_label.configure(text="")
        
        # Limpiar lista de etiquetas
        if hasattr(self, 'frame_etiquetas'):
            for widget in self.frame_etiquetas.winfo_children():
                widget.destroy()
        
        # Limpiar la imagen
        if hasattr(self, 'label_imagen'):
            self.label_imagen.configure(image="")
        
        # Recargar etiquetas
        self.actualizar_etiquetas()
        
        # Resetear estado de botones
        if hasattr(self, 'btn_reportes'):
            self.btn_reportes.configure(state='disabled')

    def crear_menu_inicio(self):
        """Crea el menú de inicio con CustomTkinter"""
    
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
    
        self.menu_frame.pack(fill="both", expand=True)
    
        main_container = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
    
        titulo = ctk.CTkLabel(
            main_container,
            text="_IC@MP_",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="#1A237E"
        )
        titulo.pack(pady=(30, 5))
    
        subtitulo = ctk.CTkLabel(
            main_container,
            text="Seleccione una herramienta para comenzar",
            font=ctk.CTkFont(size=16),
            text_color="#455A64"
        )
        subtitulo.pack(pady=(0, 30))
    
        opciones_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        opciones_frame.pack(fill="both", expand=True, padx=20)
        opciones_frame.grid_columnconfigure(0, weight=1)
        opciones_frame.grid_columnconfigure(1, weight=1)
        opciones_frame.grid_columnconfigure(2, weight=1)
        opciones_frame.grid_rowconfigure(0, weight=1)
        opciones_frame.grid_rowconfigure(1, weight=1)
    
        # ===== IESS =====
        frame_iess = ctk.CTkFrame(opciones_frame, corner_radius=15, border_width=2,
                                  border_color="#E0E0E0", fg_color="white")
        frame_iess.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
    
        tam_imagen = 150
        try:
            img_iess = Image.open(obtener_ruta_recurso("fondo_iess.png")).resize((tam_imagen, tam_imagen))
            self.tk_img_iess = ctk.CTkImage(light_image=img_iess, dark_image=img_iess, size=(tam_imagen, tam_imagen))
            ctk.CTkLabel(frame_iess, image=self.tk_img_iess, text="").pack(pady=(20, 5))
        except:
            ctk.CTkLabel(frame_iess, text="IESS", font=ctk.CTkFont(size=50, weight="bold"),
                        text_color="#1565C0").pack(pady=(20, 5))
    
        ctk.CTkLabel(frame_iess, text="IESS", font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#1565C0").pack(pady=(0, 2))
        ctk.CTkLabel(frame_iess, text="Instituto Ecuatoriano de Seguridad Social",
                    font=ctk.CTkFont(size=10), text_color="#616161").pack(pady=(0, 10))
    
        btn_iess = ctk.CTkButton(frame_iess, text="▶ Renombrar PDFs",
                                font=ctk.CTkFont(size=12, weight="bold"),
                                fg_color="#1565C0", hover_color="#0D47A1",
                                height=35, corner_radius=8,
                                command=lambda: self.seleccionar_institucion("IESS"))
        btn_iess.pack(pady=(5, 5), padx=20, fill="x")
    
        # ===== ISSFA =====
        frame_issfa = ctk.CTkFrame(opciones_frame, corner_radius=15, border_width=2,
                                   border_color="#E0E0E0", fg_color="white")
        frame_issfa.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
    
        try:
            img_issfa = Image.open(obtener_ruta_recurso("fondo_issfa.png")).resize((tam_imagen, tam_imagen))
            self.tk_img_issfa = ctk.CTkImage(light_image=img_issfa, dark_image=img_issfa, size=(tam_imagen, tam_imagen))
            ctk.CTkLabel(frame_issfa, image=self.tk_img_issfa, text="").pack(pady=(20, 5))
        except:
            ctk.CTkLabel(frame_issfa, text="ISSFA", font=ctk.CTkFont(size=50, weight="bold"),
                        text_color="#C62828").pack(pady=(20, 5))
    
        ctk.CTkLabel(frame_issfa, text="ISSFA", font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#C62828").pack(pady=(0, 2))
        ctk.CTkLabel(frame_issfa, text="Instituto de Seguridad Social de las FF.AA.",
                    font=ctk.CTkFont(size=10), text_color="#616161").pack(pady=(0, 10))
    
        btn_issfa = ctk.CTkButton(frame_issfa, text="▶ Renombrar PDFs",
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 fg_color="#C62828", hover_color="#B71C1C",
                                 height=35, corner_radius=8,
                                 command=lambda: self.seleccionar_institucion("ISSFA"))
        btn_issfa.pack(pady=(5, 5), padx=20, fill="x")
    
        # ===== UNIDOR PDF =====
        frame_unidor = ctk.CTkFrame(opciones_frame, corner_radius=15, border_width=2,
                                   border_color="#E0E0E0", fg_color="white")
        frame_unidor.grid(row=0, column=2, padx=20, pady=10, sticky="nsew")
        
        ctk.CTkLabel(frame_unidor, text="🔗", font=ctk.CTkFont(size=50)).pack(pady=(20, 5))
        ctk.CTkLabel(frame_unidor, text="UNIDOR PDF", font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#2E7D32").pack(pady=(0, 2))
        ctk.CTkLabel(frame_unidor, text="Unir PDFs por carpetas",
                    font=ctk.CTkFont(size=10), text_color="#616161").pack(pady=(0, 10))
    
        btn_unidor = ctk.CTkButton(frame_unidor, text="▶ Unir PDFs",
                                  font=ctk.CTkFont(size=12, weight="bold"),
                                  fg_color="#2E7D32", hover_color="#1B5E20",
                                  height=35, corner_radius=8,
                                  command=self.abrir_unidor)
        btn_unidor.pack(pady=(5, 5), padx=20, fill="x")
    
        # ===== PIE DE PÁGINA =====
        pie_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        pie_frame.pack(side="bottom", fill="x", pady=(10, 0))
        ctk.CTkLabel(pie_frame,
                    text=f"Versión {Actualizador.VERSION_ACTUAL} | © 2026 - Desarrollado por Mr. Sys",
                    font=ctk.CTkFont(size=10), text_color="#9E9E9E").pack(pady=10)

    def seleccionar_institucion(self, institucion):
        self.institucion_var.set(institucion)
        self.menu_frame.pack_forget()
        self.mostrar_interfaz_principal()

    def abrir_unidor(self):
        """Abrir el módulo de unión de PDFs"""
        self.menu_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        
        # Limpiar main_frame y crear el unidor
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.unidor = PDFUnidorApp(self.main_frame, self.cerrar_unidor, self)
        
    def cerrar_unidor(self):
        """Cerrar el unidor y volver al menú"""
        self.main_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)
        self.crear_menu_inicio()

    def mostrar_interfaz_principal(self):
        self.main_frame.pack(fill="both", expand=True)
        self.crear_interfaz_principal()
        self.actualizar_etiquetas()

    def crear_interfaz_principal(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
        self.main_frame.pack(fill="both", expand=True)
    
        # ===== BARRA SUPERIOR =====
        top = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        top.pack(fill="x", padx=10, pady=5)
    
        ctk.CTkLabel(top, text="Tipo de documento:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
    
        ctk.CTkRadioButton(top, text="AMB", variable=self.tipo_var, value="AMB",
                          command=self.actualizar_etiquetas, font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=5)
        ctk.CTkRadioButton(top, text="HD", variable=self.tipo_var, value="HD",
                          command=self.actualizar_etiquetas, font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=5)
        ctk.CTkRadioButton(top, text="UNIDO", variable=self.tipo_var, value="UNIDO",
                          command=self.actualizar_etiquetas, font=ctk.CTkFont(size=12)).grid(row=0, column=3, padx=5)
    
        ctk.CTkLabel(top, text="Ruta:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w")
    
        self.ruta_entry = ctk.CTkEntry(top, width=400, height=30)
        self.ruta_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
    
        ctk.CTkButton(top, text="Seleccionar", fg_color="#1976D2", hover_color="#1565C0",
                     height=30, width=100, command=self.seleccionar_ruta).grid(row=1, column=4, padx=5)
    
        # ===== ÁREA PRINCIPAL =====
        medio = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        medio.pack(fill="both", expand=True, padx=5, pady=5)
    
        # ===== PANEL IZQUIERDO =====
        panel_izquierdo = ctk.CTkFrame(medio, width=350, fg_color="#F5F7FA")
        panel_izquierdo.pack(side="left", fill="both", padx=5, pady=5)
        panel_izquierdo.pack_propagate(False)
    
        contenedor_etiquetas = ctk.CTkFrame(panel_izquierdo, fg_color="transparent")
        contenedor_etiquetas.pack(fill="both", expand=True, padx=5, pady=5)
        contenedor_etiquetas.grid_columnconfigure(0, weight=1)
        contenedor_etiquetas.grid_rowconfigure(0, weight=1)
    
        scroll_etiquetas = ctk.CTkScrollableFrame(contenedor_etiquetas, fg_color="transparent")
        scroll_etiquetas.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.frame_etiquetas = scroll_etiquetas
    
        frame_hoja_blanca = ctk.CTkFrame(contenedor_etiquetas, fg_color="#FFF3E0", corner_radius=8, border_width=1, border_color="#FFE0B2")
        frame_hoja_blanca.grid(row=0, column=1, sticky="ns", padx=(0, 0))
    
        btn_hoja_blanca = ctk.CTkButton(
            frame_hoja_blanca,
            text="📄\nH\nO\nJ\nA\n\nB\nL\nA\nN\nC\nA",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="transparent",
            text_color="#E65100",
            hover_color="#FFE0B2",
            width=35,
            height=400,
            corner_radius=6,
            command=lambda: self.etiquetar_pagina("HOJA BLANCA")
        )
        btn_hoja_blanca.pack(fill="both", expand=True, padx=3, pady=3)
        self.btn_hoja_blanca = btn_hoja_blanca
    
        # ===== PANEL DE FUNCIONES (BOTONES EN 2 COLUMNAS) =====
        scroll_funciones = ctk.CTkScrollableFrame(panel_izquierdo, fg_color="transparent", height=200)
        scroll_funciones.pack(fill="both", expand=True, padx=5, pady=5)
        self.frame_funciones = scroll_funciones
    
        # ===== PANEL DERECHO =====
        self.panel_imagen = ctk.CTkFrame(medio, fg_color="white", corner_radius=10,
                                     border_width=1, border_color="#E0E0E0")
        self.panel_imagen.pack(side="right", expand=True, fill="both", padx=5, pady=5)
    
        self.canvas_img = ctk.CTkCanvas(self.panel_imagen, bg="white", highlightthickness=0)
        self.canvas_img.pack(fill="both", expand=True)
    
        self.label_imagen = ctk.CTkLabel(self.canvas_img, text="", fg_color="transparent")
        self.label_imagen.place(relx=0.5, rely=0.5, anchor="center")
    
        self.botones_etiqueta = []
        self.crear_botones_funciones()
    
        # ===== BARRA DE PROGRESO (ARRIBA DE LOS BOTONES) =====
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        info_frame.pack(side="bottom", fill="x", padx=10, pady=5)
    
        self.info_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=10))
        self.info_label.pack(side="left", padx=5)
    
        self.progress_bar = ctk.CTkProgressBar(info_frame, height=10, width=300)
        self.progress_bar.pack(side="left", padx=10, expand=True, fill="x")
        self.progress_bar.set(0)
    
        self.progreso_texto = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=10, weight="bold"),
                                           text_color="#1976D2")
        self.progreso_texto.pack(side="right", padx=5)
        
        # ===== BOTONES INFERIORES (ABAJO DE LA BARRA DE PROGRESO) =====
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Botón Regresar al menú (IZQUIERDA)
        btn_regresar_menu = ctk.CTkButton(
            bottom_frame, 
            text="🔙 Regresar al menú",
            fg_color="#78909C", 
            hover_color="#546E7A",
            height=30, 
            width=140,
            command=self.regresar_al_menu
        )
        btn_regresar_menu.pack(side=tk.LEFT, padx=5)
        
        # Botón Reportes (DERECHA)
        self.btn_reportes = ctk.CTkButton(
            bottom_frame, 
            text="📊 Reportes",
            fg_color="#2E7D32", 
            hover_color="#1B5E20",
            height=30, 
            width=120,
            command=self.abrir_reportes,
            state='disabled'
        )
        self.btn_reportes.pack(side=tk.RIGHT, padx=5)

    def actualizar_etiquetas(self):
        for b in self.botones_etiqueta:
            b.destroy()
        self.botones_etiqueta.clear()

        etiquetas = ETIQUETAS.get(self.institucion_var.get(), {}).get(self.tipo_var.get(), [])
        etiquetas = [et for et in etiquetas if et.upper() != "HOJA BLANCA"]

        for et in etiquetas:
            btn = ctk.CTkButton(
                self.frame_etiquetas, 
                text=et, 
                font=ctk.CTkFont(size=11),
                fg_color="#E3F2FD",
                text_color="#1A237E",
                hover_color="#BBDEFB",
                height=28,
                corner_radius=4,
                anchor="w",
                command=lambda e=et: self.etiquetar_pagina(e)
            )
            btn.pack(pady=2, fill="x", padx=5)
            self.botones_etiqueta.append(btn)

    def crear_botones_funciones(self):
        """Crea los botones de funciones en 2 columnas y más cortos"""
        botones = [
            ("⟲ Girar Izq", lambda: self.rotar_pagina(-90)),
            ("Girar Der ⟳", lambda: self.rotar_pagina(90)),
            ("Pág siguiente ⏭", self.pagina_siguiente),
            ("⏮ Pág anterior", self.pagina_anterior),
            ("❌ Eliminar pág", self.previsualizar_eliminar_paginas),
            ("📄 Mover pág", self.previsualizar_mover_paginas),
            ("📂 Revisar PDF", self.revisar_pdf_anterior),
            ("⛔ Omitir PDF", self.omitir_pdf)
        ]
    
        grid_frame = ctk.CTkFrame(self.frame_funciones, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
    
        for idx, (texto, comando) in enumerate(botones):
            row = idx // 2
            col = idx % 2
            
            if "Eliminar" in texto:
                fg_color, hover_color = "#D32F2F", "#B71C1C"
            elif "Omitir" in texto:
                fg_color, hover_color = "#757575", "#616161"
            elif "Revisar" in texto:
                fg_color, hover_color = "#1976D2", "#1565C0"
            else:
                fg_color, hover_color = "#455A64", "#37474F"
        
            btn = ctk.CTkButton(
                grid_frame, 
                text=texto, 
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=fg_color, 
                hover_color=hover_color,
                height=32,
                width=130,
                corner_radius=6, 
                command=comando
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")

    def seleccionar_ruta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_entry.delete(0, tk.END)
            self.ruta_entry.insert(0, ruta)
            self.ruta_escaneda = ruta
            self.obtener_pdfs(ruta)

    def obtener_pdfs(self, base):
        self.pdfs.clear()
        pdfs_encontrados = []
        carpetas_omitidas = []
        carpetas_validas = []

        for raiz, dirs, archivos in os.walk(base):
            dirs.sort(key=natural_sort_key)

            pdfs = [f for f in archivos if f.lower().endswith(".pdf")]

            if len(pdfs) == 1:

                archivo = pdfs[0]
                ruta_pdf = os.path.join(raiz, archivo)

                nombre_base = os.path.splitext(archivo)[0]
                carpeta_procesada = os.path.join(raiz, nombre_base)

                if not os.path.exists(carpeta_procesada):
                    pdfs_encontrados.append(ruta_pdf)
                    carpetas_validas.append(os.path.basename(raiz))

            else:
                carpetas_omitidas.append(
                    (os.path.basename(raiz), raiz, len(pdfs))
                )

        pdfs_encontrados.sort(key=natural_sort_key)

        self.pdfs = pdfs_encontrados
        self.total_pdfs = len(self.pdfs)

        # Generar reporte en la carpeta de reportes
        self.generar_reporte_escaneo(base, carpetas_validas, carpetas_omitidas)

        continuar = messagebox.askyesno(
            "Resultado del escaneo",
            f"Escaneo finalizado.\n\n"
            f"Carpetas válidas: {len(self.pdfs)}\n"
            f"Carpetas omitidas: {len(carpetas_omitidas)}\n\n"
            f"Se generó el reporte en la carpeta 'Reportes'\n\n"
            f"¿Desea comenzar el procesamiento?"
        )

        if not continuar:
            self.limpiar_interfaz_completa()
            return

        self.pdf_index = -1

        if self.pdfs:
            self.cargar_siguiente_pdf()
        else:
            messagebox.showinfo(
                "Información",
                "No se encontraron carpetas con un único PDF para procesar."
            )
            self.limpiar_interfaz_completa()

    def generar_reporte_escaneo(self, base, carpetas_validas, carpetas_omitidas):
        """Genera el reporte del escaneo con fecha y hora"""
        try:
            fecha_hora = datetime.now()
            fecha_str = fecha_hora.strftime("%Y-%m-%d_%H-%M-%S")
            
            institucion = self.institucion_var.get()
            tipo = self.tipo_var.get()
            
            carpeta_reportes = obtener_ruta_reportes()
            nombre_reporte = f"Reporte_{institucion}_{tipo}_{fecha_str}.txt"
            ruta_reporte = os.path.join(carpeta_reportes, nombre_reporte)
            
            with open(ruta_reporte, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"REPORTE DE ESCANEO - {institucion} - {tipo}\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Fecha: {fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Carpeta escaneada: {base}\n")
                f.write(f"Institución: {institucion}\n")
                f.write(f"Tipo: {tipo}\n\n")
                f.write("-" * 80 + "\n")
                f.write("RESUMEN\n")
                f.write("-" * 80 + "\n")
                f.write(f"Carpetas válidas (1 PDF): {len(carpetas_validas)}\n")
                f.write(f"Carpetas omitidas: {len(carpetas_omitidas)}\n\n")
                
                if carpetas_validas:
                    f.write("-" * 80 + "\n")
                    f.write("CARPETAS VÁLIDAS\n")
                    f.write("-" * 80 + "\n")
                    for carpeta in carpetas_validas:
                        f.write(f"  ✅ {carpeta}\n")
                    f.write("\n")
                
                if carpetas_omitidas:
                    f.write("-" * 80 + "\n")
                    f.write("CARPETAS OMITIDAS\n")
                    f.write("-" * 80 + "\n")
                    for carpeta, ruta, cantidad in carpetas_omitidas:
                        if cantidad == 0:
                            motivo = "No contiene archivos PDF"
                        else:
                            motivo = f"Contiene {cantidad} archivos PDF"
                        f.write(f"  ⏭️ {carpeta} - {motivo}\n")
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("FIN DEL REPORTE\n")
                f.write("=" * 80 + "\n")
            
            # Habilitar botón de reportes
            self.btn_reportes.configure(state='normal')
            
        except Exception as e:
            print(f"Error al generar reporte: {e}")

    def cargar_siguiente_pdf(self):
        self.pdf_index += 1
        if self.pdf_index >= len(self.pdfs):
            messagebox.showinfo("Listo", "Todos los archivos han sido procesados.")
            self.progress_bar.set(1)
            self.progreso_texto.configure(text="100%")
            self.limpiar_interfaz_completa()
            return
            
        self.path_pdf = self.pdfs[self.pdf_index]
        self.actual_pdf = self.pdf_index + 1
        
        try:
            self.cerrar_documento_seguro()
            
            self.doc = fitz.open(self.path_pdf)
            self.page_index = 0
            self.page_etiquetas = {}
            self.deleted_pages = set()
            
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
        if self.total_pdfs > 0 and self.verificar_documento_abierto():
            porcentaje = (self.actual_pdf / self.total_pdfs)
            self.progress_bar.set(porcentaje)
            
            nombre_archivo = os.path.basename(self.path_pdf)
            if len(nombre_archivo) > 30:
                nombre_archivo = nombre_archivo[:27] + "..."
            
            total_paginas = len(self.doc)
            carpeta = os.path.basename(os.path.dirname(self.path_pdf))
            
            self.info_label.configure(text=f"📁 {carpeta} | 📄 {nombre_archivo} | Página {self.page_index + 1} de {total_paginas}")
            self.progreso_texto.configure(text=f"{self.actual_pdf}/{self.total_pdfs}")

    def mostrar_pagina(self):
        if not self.verificar_documento_abierto():
            return
    
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
            
        real_index = self.orden_paginas[self.page_index]
        rot = self.rotacion_actual.get(real_index, 0)
        page = self.doc[real_index]
        
        rot_original = page.rotation
        page.set_rotation(0)
        mat = fitz.Matrix(1, 1).prerotate(rot)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        page.set_rotation(rot_original)
        
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
            nuevo_ancho, nuevo_alto = img.size
        
        self.tk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(nuevo_ancho, nuevo_alto))
        self.label_imagen.configure(image=self.tk_img)
        
        self.actualizar_progreso()

    def etiquetar_pagina(self, etiqueta):
        if not self.verificar_documento_abierto():
            return
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
        real_index = self.orden_paginas[self.page_index]
        self.page_etiquetas[real_index] = etiqueta
        self.pagina_siguiente()

    def eliminar_pagina(self):
        if not self.verificar_documento_abierto():
            return
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
        real_index = self.orden_paginas[self.page_index]
        self.deleted_pages.add(real_index)
        self.pagina_siguiente()

    def rotar_pagina(self, angulo):
        if not self.verificar_documento_abierto():
            return
        if not self.orden_paginas or self.page_index >= len(self.orden_paginas):
            return
        real_index = self.orden_paginas[self.page_index]
        self.rotacion_actual[real_index] = (
            self.rotacion_actual.get(real_index, 0) + angulo
        ) % 360
        self.mostrar_pagina()

    def pagina_siguiente(self):
        try:
            if not self.verificar_documento_abierto():
                self.cargar_siguiente_pdf()
                return
                
            if self.page_index < len(self.orden_paginas) - 1:
                self.page_index += 1
                self.mostrar_pagina()
            else:
                self.guardar_etiquetas()
                self.cargar_siguiente_pdf()
        except Exception as e:
            print(f"Error en pagina_siguiente: {e}")
            self.cargar_siguiente_pdf()

    def pagina_anterior(self):
        if not self.verificar_documento_abierto():
            return
        if self.page_index > 0:
            self.page_index -= 1
            self.mostrar_pagina()

    def omitir_pdf(self):
        self.cerrar_documento_seguro()
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
        if not self.verificar_documento_abierto():
            messagebox.showerror("Error", "No hay un documento abierto para mover páginas.")
            return
            
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

        if not self.verificar_documento_abierto():
            try:
                self.doc = fitz.open(self.path_pdf)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el documento: {e}")
                mover_win.destroy()
                return

        self.selected_pages = set()
        self.thumbnails_widgets = []
        self.drag_data = {"item": None, "x": 0, "y": 0, "ghost": None}

        def toggle_selection(page_num, container):
            if page_num in self.selected_pages:
                self.selected_pages.remove(page_num)
                container.configure(highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            else:
                self.selected_pages.add(page_num)
                container.configure(highlightbackground="red", highlightcolor="red", highlightthickness=3)

        def on_thumbnail_click(event, page_num, container):
            ctrl_pressed = (event.state & 0x4) == 0x4
            
            if ctrl_pressed:
                toggle_selection(page_num, container)
            else:
                for p, c in self.thumbnails_widgets:
                    if p in self.selected_pages:
                        c.configure(highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
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
                try:
                    page = self.doc[page_num]
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
                    cont.configure(highlightbackground="red", highlightcolor="red", highlightthickness=3)
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
                new_doc.insert_pdf(self.doc, from_page=old_idx, to_page=old_idx)
                rot = self.rotacion_actual.get(old_idx, 0)
                if rot != 0:
                    last_page = new_doc[-1]
                    last_page.set_rotation(rot)

            self.cerrar_documento_seguro()
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
        if not self.verificar_documento_abierto():
            messagebox.showerror("Error", "No hay un documento abierto para eliminar páginas.")
            return
            
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
        
        if not self.verificar_documento_abierto():
            try:
                self.doc = fitz.open(self.path_pdf)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el documento: {e}")
                eliminar_win.destroy()
                return

        self.selected_pages = set()
        self.thumbnails_widgets = []

        def toggle_selection(page_num, container):
            if page_num in self.selected_pages:
                self.selected_pages.remove(page_num)
                container.configure(highlightbackground="gray", highlightthickness=1)
            else:
                self.selected_pages.add(page_num)
                container.configure(highlightbackground="red", highlightthickness=3)

        def on_click(event, page_num, container):
            ctrl = (event.state & 0x4) == 0x4
            if not ctrl:
                for p, c in self.thumbnails_widgets:
                    c.configure(highlightbackground="gray", highlightthickness=1)
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
                try:
                    page = self.doc[page_num]
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
                    cont.configure(highlightbackground="red", highlightthickness=3)
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
            
            self.cerrar_documento_seguro()
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
        if not self.verificar_documento_abierto():
            return
            
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
        """Regresa al menú principal cerrando el documento de forma segura"""
        self.cerrar_documento_seguro()
        self.main_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)
        self.crear_menu_inicio()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFApp(root)
    root.mainloop()
