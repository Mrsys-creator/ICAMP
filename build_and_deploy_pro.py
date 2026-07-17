"""
BUILD & DEPLOY PROFESIONAL PARA ICAMP - VERSIÓN AUTOMÁTICA
-----------------------------------
HACE TODO AUTOMÁTICAMENTE:
1. git pull (trae cambios de GitHub)
2. Detecta e instala librerías
3. Actualiza app.py y version.json
4. Compila EXE
5. Crea instalador profesional
6. git commit y git push (sube cambios a GitHub)
7. Crea release y sube EXE a GitHub

USO: python build_and_deploy_pro.py
"""

import os
import sys
import re
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading
import shutil

class BuildDeployPro:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Build & Deploy PRO - ICAMP")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # ===== CONFIGURACIÓN =====
        self.github_repo = "Mrsys-creator/ICAMP"
        self.nombre_app = "ICAMP"
        self.nombre_exe = "RenombradorPDF.exe"
        self.empresa = "Mr. Sys"
        self.sitio_web = "https://github.com/Mrsys-creator/ICAMP"
        
        # Variables
        self.ruta_app = tk.StringVar()
        self.nueva_version = tk.StringVar()
        self.mensaje_cambios = tk.StringVar()
        self.progreso = tk.DoubleVar()
        self.idiomas = {"es": True, "en": True}
        
        # Detectar Python
        self.python_version = sys.version_info
        self.es_python_314 = self.python_version.major == 3 and self.python_version.minor >= 14
        self.python_paths = self.buscar_python_compatible()
        
        self.version_actual = self.obtener_version_actual()
        self.librerias_detectadas = []
        
        self.create_widgets()
        
    def buscar_python_compatible(self):
        paths = []
        posibles = [
            r"C:\Python313\python.exe",
            r"C:\Python312\python.exe",
            r"C:\Program Files\Python313\python.exe",
            r"C:\Program Files\Python312\python.exe",
            r"C:\Users\{}\AppData\Local\Programs\Python\Python313\python.exe".format(os.getlogin()),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python312\python.exe".format(os.getlogin()),
        ]
        for p in posibles:
            if os.path.exists(p):
                paths.append(p)
        return paths
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="🚀 BUILD & DEPLOY PRO - ICAMP", font=("Arial", 18, "bold"))
        titulo.pack(pady=10)
        
        if self.es_python_314:
            warn_frame = ttk.Frame(main_frame, relief="solid", borderwidth=2)
            warn_frame.pack(fill="x", pady=5)
            ttk.Label(warn_frame, text="⚠️ PYTHON 3.14 - Usando Python 3.13 para compilar", 
                     foreground="orange", font=("Arial", 11)).pack(pady=5)
        
        # Información
        info_frame = ttk.LabelFrame(main_frame, text="📊 Información", padding="10")
        info_frame.pack(fill="x", pady=5)
        ttk.Label(info_frame, text=f"📂 Versión actual: {self.version_actual}").pack(anchor="w")
        ttk.Label(info_frame, text=f"📁 Repositorio: {self.github_repo}").pack(anchor="w")
        
        # Carpeta
        ttk.Label(main_frame, text="📁 Carpeta del proyecto:").pack(anchor="w", pady=(10, 0))
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill="x", pady=5)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.ruta_app, width=50)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="📂 Buscar", command=self.seleccionar_carpeta).pack(side="right")
        
        # Versión
        ttk.Label(main_frame, text="🔢 Nueva versión (ej: 1.1.2):").pack(anchor="w", pady=(10, 0))
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill="x", pady=5)
        self.version_entry = ttk.Entry(version_frame, textvariable=self.nueva_version, width=25)
        self.version_entry.pack(side="left")
        ttk.Label(version_frame, text=f"  Actual: {self.version_actual}", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        # Mensaje de cambios
        ttk.Label(main_frame, text="📝 Mensaje de cambios:").pack(anchor="w", pady=(10, 0))
        self.mensaje_entry = ttk.Entry(main_frame, textvariable=self.mensaje_cambios, width=70)
        self.mensaje_entry.pack(fill="x", pady=5)
        self.mensaje_entry.insert(0, "Nueva versión con mejoras y actualizaciones")
        
        # Detectar librerías
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="🔍 Detectar librerías", command=self.detectar_librerias).pack(side="left", padx=5)
        self.librerias_label = ttk.Label(btn_frame, text="", font=("Arial", 9))
        self.librerias_label.pack(side="left", padx=10)
        
        # Idiomas
        idiomas_frame = ttk.LabelFrame(main_frame, text="🌐 Idiomas del instalador", padding="10")
        idiomas_frame.pack(fill="x", pady=10)
        
        self.idioma_es = tk.BooleanVar(value=True)
        self.idioma_en = tk.BooleanVar(value=True)
        ttk.Checkbutton(idiomas_frame, text="🇪🇸 Español", variable=self.idioma_es).pack(side="left", padx=10)
        ttk.Checkbutton(idiomas_frame, text="🇬🇧 English", variable=self.idioma_en).pack(side="left", padx=10)
        
        # Opciones
        opciones_frame = ttk.LabelFrame(main_frame, text="⚙️ Opciones", padding="10")
        opciones_frame.pack(fill="x", pady=10)
        
        self.upload_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="📤 Subir a GitHub", variable=self.upload_var).pack(anchor="w")
        
        self.installer_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="📦 Crear instalador profesional", variable=self.installer_var).pack(anchor="w")
        
        self.auto_install_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="🔧 Instalar librerías automáticamente", variable=self.auto_install_var).pack(anchor="w")
        
        # Progreso
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progreso, maximum=100, length=600)
        self.progress_bar.pack(fill="x", pady=10)
        self.status_label = ttk.Label(main_frame, text="✅ Listo", font=("Arial", 10))
        self.status_label.pack(anchor="w", pady=5)
        
        # Botones
        btn_accion = ttk.Frame(main_frame)
        btn_accion.pack(fill="x", pady=10)
        self.build_btn = ttk.Button(btn_accion, text="🚀 INICIAR BUILD & DEPLOY PRO", 
                                   command=self.iniciar_proceso)
        self.build_btn.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(btn_accion, text="❌ Cerrar", command=self.root.destroy).pack(side="right", padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding="5")
        log_frame.pack(fill="both", expand=True, pady=10)
        self.log_text = tk.Text(log_frame, height=12, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)
        
    def log(self, msg, tipo="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colores = {"info": "black", "success": "green", "error": "red", "warning": "orange", "github": "blue"}
        color = colores.get(tipo, "black")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n")
        self.log_text.see("end")
        self.root.update()
        
    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.ruta_app.set(carpeta)
            if os.path.exists(os.path.join(carpeta, "app.py")):
                self.log("✅ app.py encontrado", "success")
                self.version_actual = self.obtener_version_actual()
                self.log(f"📌 Versión actual: {self.version_actual}", "info")
                self.detectar_librerias()
                
    def obtener_version_actual(self):
        try:
            ruta = os.path.join(self.ruta_app.get(), "app.py")
            if not os.path.exists(ruta):
                return "0.0.0"
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            match = re.search(r'VERSION_ACTUAL\s*=\s*["\']([\d.]+)["\']', contenido)
            return match.group(1) if match else "0.0.0"
        except:
            return "0.0.0"
    
    def detectar_librerias(self):
        try:
            ruta = os.path.join(self.ruta_app.get(), "app.py")
            if not os.path.exists(ruta):
                return
            
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            
            librerias_conocidas = {
                "cv2": "opencv-python",
                "tensorflow": "tensorflow",
                "torch": "torch",
                "sklearn": "scikit-learn",
                "pandas": "pandas",
                "numpy": "numpy",
                "pytesseract": "pytesseract",
                "easyocr": "easyocr",
                "transformers": "transformers",
                "PIL": "Pillow",
                "customtkinter": "customtkinter",
                "PyPDF2": "PyPDF2",
                "fitz": "PyMuPDF",
                "openpyxl": "openpyxl",
                "xlsxwriter": "xlsxwriter",
                "matplotlib": "matplotlib",
                "seaborn": "seaborn",
                "plotly": "plotly",
                "requests": "requests"
            }
            
            imports = re.findall(r'^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)', contenido, re.MULTILINE)
            
            self.librerias_detectadas = []
            for imp in imports:
                if imp in librerias_conocidas:
                    lib = librerias_conocidas[imp]
                    if lib not in self.librerias_detectadas:
                        self.librerias_detectadas.append(lib)
            
            if self.librerias_detectadas:
                self.librerias_label.config(text=f"📦 {', '.join(self.librerias_detectadas)}")
                self.log(f"📦 Librerías detectadas: {', '.join(self.librerias_detectadas)}", "success")
            else:
                self.librerias_label.config(text="✅ Sin librerías adicionales")
            return self.librerias_detectadas
        except Exception as e:
            self.log(f"⚠️ Error: {e}", "warning")
            return []
    
    # ===== Sincronizar con GitHub AUTOMÁTICAMENTE =====
    def git_sync(self):
        """Sincroniza automáticamente con GitHub (pull + commit + push)"""
        try:
            carpeta = self.ruta_app.get()
            
            self.log("🔄 Sincronizando con GitHub...", "github")
            
            # 1. Verificar si hay cambios sin commitear
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         cwd=carpeta, capture_output=True, text=True)
            
            # 2. Si hay cambios, hacer commit
            if status_result.stdout.strip():
                self.log("📝 Hay cambios locales, guardando...", "info")
                subprocess.run(["git", "add", "."], cwd=carpeta, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"Actualizar antes de build {datetime.now().strftime('%Y-%m-%d %H:%M')}"], 
                             cwd=carpeta, check=True, capture_output=True)
                self.log("✅ Cambios locales guardados", "success")
            
            # 3. Traer cambios de GitHub
            self.log("📥 Descargando cambios de GitHub...", "github")
            pull_result = subprocess.run(["git", "pull", "origin", "main", "--rebase"], 
                                       cwd=carpeta, capture_output=True, text=True)
            
            if "Already up to date" in pull_result.stdout:
                self.log("ℹ️ Ya estás al día con GitHub", "info")
            else:
                self.log("✅ Cambios descargados de GitHub", "success")
            
            return True
            
        except Exception as e:
            self.log(f"⚠️ Error al sincronizar: {e}", "warning")
            return False
    
    def git_push_changes(self, nueva_version):
        """Sube los cambios a GitHub automáticamente"""
        try:
            carpeta = self.ruta_app.get()
            
            self.log("📤 Subiendo cambios a GitHub...", "github")
            
            # 1. Agregar archivos
            subprocess.run(["git", "add", "app.py", "version.json"], cwd=carpeta, check=True, capture_output=True)
            
            # 2. Commit
            commit_msg = f"Actualizar a versión {nueva_version}: {self.mensaje_cambios.get() or 'Nueva versión'}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=carpeta, check=True, capture_output=True)
            self.log(f"✅ Commit creado: {commit_msg}", "success")
            
            # 3. Pull antes de push (por si hay cambios remotos)
            self.log("📥 Verificando cambios remotos...", "github")
            subprocess.run(["git", "pull", "origin", "main", "--rebase"], 
                         cwd=carpeta, check=True, capture_output=True)
            
            # 4. Push
            self.log("📤 Subiendo a GitHub...", "github")
            subprocess.run(["git", "push", "-u", "origin", "main"], 
                         cwd=carpeta, check=True, capture_output=True)
            self.log("✅ Cambios subidos a GitHub", "success")
            
            return True
            
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in str(e.stderr) or "no changes added" in str(e.stderr):
                self.log("ℹ️ No hay cambios nuevos para subir", "info")
                return True
            else:
                self.log(f"⚠️ Error en git: {e}", "warning")
                return False
        except Exception as e:
            self.log(f"⚠️ Error al subir cambios: {e}", "warning")
            return False
    
    def actualizar_version_en_codigo(self, nueva_version):
        """Actualiza la versión en app.py y version.json"""
        try:
            carpeta = self.ruta_app.get()
            
            # 1. Actualizar app.py
            ruta_app = os.path.join(carpeta, "app.py")
            with open(ruta_app, "r", encoding="utf-8") as f:
                contenido = f.read()
            
            contenido = re.sub(
                r'(VERSION_ACTUAL\s*=\s*["\'])[\d.]+(["\'])',
                f'VERSION_ACTUAL = "{nueva_version}"',
                contenido
            )
            
            contenido = re.sub(
                r'(version\s*=\s*["\'])[\d.]+(["\'])',
                f'version = "{nueva_version}"',
                contenido
            )
            
            with open(ruta_app, "w", encoding="utf-8") as f:
                f.write(contenido)
            
            self.log(f"✅ app.py actualizado a versión {nueva_version}", "success")
            
            # 2. Actualizar version.json
            ruta_json = os.path.join(carpeta, "version.json")
            version_data = {
                "version": nueva_version,
                "mensaje": self.mensaje_cambios.get() or f"Versión {nueva_version}",
                "url_descarga": f"https://github.com/{self.github_repo}/releases/download/v{nueva_version}/RenombradorPDF.exe",
                "url_app": f"https://raw.githubusercontent.com/{self.github_repo}/main/app.py",
                "nuevas_librerias": self.librerias_detectadas,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(ruta_json, "w", encoding="utf-8") as f:
                json.dump(version_data, f, indent=4, ensure_ascii=False)
            
            self.log(f"✅ version.json actualizado a versión {nueva_version}", "success")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error al actualizar versión: {e}", "error")
            return False
    
    def compilar_exe(self):
        try:
            self.log("📦 Compilando EXE...", "info")
            self.progreso.set(20)
            
            carpeta = self.ruta_app.get()
            
            # Determinar Python
            python_exe = sys.executable
            if self.es_python_314 and self.python_paths:
                python_exe = self.python_paths[0]
                self.log(f"🐍 Usando: {os.path.basename(python_exe)}", "info")
            
            # Instalar PyInstaller
            try:
                subprocess.run([python_exe, "-m", "pip", "install", "pyinstaller", "--upgrade"], 
                             check=True, capture_output=True)
            except:
                self.log("📦 Instalando PyInstaller...", "info")
                subprocess.run([python_exe, "-m", "pip", "install", "pyinstaller"], 
                             check=True, capture_output=True)
            
            # Comando
            cmd = [
                python_exe, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name", "RenombradorPDF",
                "--clean",
                "--noconfirm",
                os.path.join(carpeta, "app.py")
            ]
            
            # Icono
            icono = os.path.join(carpeta, "tu_icono.ico")
            if os.path.exists(icono):
                cmd.insert(4, "--icon")
                cmd.insert(5, icono)
                self.log("✅ Icono incluido", "success")
            
            # Imágenes
            for img in ["fondo_iess.png", "fondo_issfa.png"]:
                if os.path.exists(os.path.join(carpeta, img)):
                    cmd.insert(4, "--add-data")
                    cmd.insert(5, f"{img};.")
                    self.log(f"✅ {img} incluido", "success")
            
            # Ejecutar
            self.log("🔨 Compilando... (esto puede tomar varios minutos)", "info")
            resultado = subprocess.run(cmd, cwd=carpeta, capture_output=True, text=True)
            
            if resultado.returncode != 0:
                self.log("❌ Error en compilación:", "error")
                self.log(resultado.stderr, "error")
                return False
            
            exe_path = os.path.join(carpeta, "dist", "RenombradorPDF.exe")
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / (1024*1024)
                self.log(f"✅ EXE compilado: {size:.2f} MB", "success")
                return True
            
            self.log("❌ No se encontró el EXE", "error")
            return False
        except Exception as e:
            self.log(f"❌ Error: {e}", "error")
            return False
    
    def crear_instalador_profesional(self, nueva_version):
        """Crea un instalador profesional con múltiples idiomas y todos los archivos"""
        try:
            if not self.installer_var.get():
                return True
            
            self.log("📦 Creando instalador profesional...", "info")
            self.progreso.set(80)
            
            carpeta = self.ruta_app.get()
            exe_path = os.path.join(carpeta, "dist", "RenombradorPDF.exe")
            
            if not os.path.exists(exe_path):
                self.log("❌ No se encontró el EXE", "error")
                return False
            
            # Crear carpeta para archivos del instalador
            installer_files = os.path.join(carpeta, "Installer_Files")
            os.makedirs(installer_files, exist_ok=True)
            
            # Copiar archivos necesarios
            shutil.copy(exe_path, os.path.join(installer_files, "RenombradorPDF.exe"))
            
            # Copiar version.json
            json_path = os.path.join(carpeta, "version.json")
            if os.path.exists(json_path):
                shutil.copy(json_path, os.path.join(installer_files, "version.json"))
            
            # Copiar imágenes
            for img in ["fondo_iess.png", "fondo_issfa.png", "tu_icono.ico"]:
                src = os.path.join(carpeta, img)
                if os.path.exists(src):
                    shutil.copy(src, os.path.join(installer_files, img))
                    self.log(f"✅ {img} copiado", "success")
            
            # Script de Inno Setup
            self.log("📝 Generando script de Inno Setup...", "info")
            
            # Idiomas
            idiomas_seleccionados = []
            if self.idioma_es.get():
                idiomas_seleccionados.append('Name: "es"; MessagesFile: "compiler:Languages\\Spanish.isl"')
            if self.idioma_en.get():
                idiomas_seleccionados.append('Name: "en"; MessagesFile: "compiler:Default.isl"')
            
            idiomas_str = "\n  ".join(idiomas_seleccionados) if idiomas_seleccionados else 'Name: "es"; MessagesFile: "compiler:Languages\\Spanish.isl"'
            
            # AppId con escape correcto
            app_id = f"{{{{{self.nombre_app}-{nueva_version.replace('.', '-')}-PRO}}}}"
            
            iss_content = f'''
; Script de instalación para ICAMP
; Versión: {nueva_version}

[Setup]
AppId={app_id}
AppName={self.nombre_app}
AppVersion={nueva_version}
AppPublisher={self.empresa}
AppPublisherURL={self.sitio_web}
AppSupportURL={self.sitio_web}
AppUpdatesURL={self.sitio_web}
DefaultDirName={{pf}}\\{self.nombre_app}
DefaultGroupName={self.nombre_app}
AllowNoIcons=yes
OutputDir={carpeta}\\Installer_PRO
OutputBaseFilename=ICAMP_Setup_{nueva_version}
SetupIconFile={os.path.join(installer_files, "tu_icono.ico")}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={{app}}\\RenombradorPDF.exe
UninstallDisplayName={self.nombre_app} {nueva_version}

[Languages]
{idiomas_str}

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "{os.path.join(installer_files, "RenombradorPDF.exe")}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{os.path.join(installer_files, "version.json")}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{os.path.join(installer_files, "fondo_iess.png")}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{os.path.join(installer_files, "fondo_issfa.png")}"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{self.nombre_app}"; Filename: "{{app}}\\RenombradorPDF.exe"
Name: "{{group}}\\Desinstalar {self.nombre_app}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{self.nombre_app}"; Filename: "{{app}}\\RenombradorPDF.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\RenombradorPDF.exe"; Description: "{{cm:LaunchProgram,{self.nombre_app}}}"; Flags: postinstall nowait skipifsilent

[Messages]
SpanishWelcomeLabel1=Bienvenido al instalador de {self.nombre_app}
SpanishWelcomeLabel2=Este programa instalará {self.nombre_app} versión {nueva_version} en tu sistema.
SpanishReadyLabel1=Listo para instalar {self.nombre_app}
SpanishReadyLabel2=El programa está listo para ser instalado en tu sistema.

EnglishWelcomeLabel1=Welcome to {self.nombre_app} Setup
EnglishWelcomeLabel2=This will install {self.nombre_app} version {nueva_version} on your system.
EnglishReadyLabel1=Ready to install {self.nombre_app}
EnglishReadyLabel2=The program is ready to be installed on your system.
'''

            # Guardar script
            iss_path = os.path.join(carpeta, "installer_pro.iss")
            with open(iss_path, "w", encoding="utf-8") as f:
                f.write(iss_content)
            
            # Buscar Inno Setup
            inno_paths = [
                r"C:\Program Files (x86)\Inno Setup 6\iscc.exe",
                r"C:\Program Files\Inno Setup 6\iscc.exe"
            ]
            
            inno_exe = None
            for path in inno_paths:
                if os.path.exists(path):
                    inno_exe = path
                    break
            
            if not inno_exe:
                self.log("⚠️ Inno Setup no instalado", "warning")
                self.log("📌 Descarga desde: https://jrsoftware.org/isdl.php", "warning")
                return False
            
            # Compilar instalador
            self.log("🔨 Compilando instalador...", "info")
            resultado = subprocess.run([inno_exe, iss_path], capture_output=True, text=True)
            
            if resultado.returncode != 0:
                self.log("❌ Error al compilar instalador:", "error")
                self.log(resultado.stderr, "error")
                return False
            
            self.log("✅ Instalador profesional creado exitosamente!", "success")
            
            installer_path = os.path.join(carpeta, "Installer_PRO", f"ICAMP_Setup_{nueva_version}.exe")
            if os.path.exists(installer_path):
                size = os.path.getsize(installer_path) / (1024*1024)
                self.log(f"📦 Instalador: {installer_path} ({size:.2f} MB)", "success")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error al crear instalador: {e}", "error")
            return False
    
    def subir_a_github_automatico(self, nueva_version):
        """Sube TODO automáticamente a GitHub usando gh CLI"""
        try:
            if not self.upload_var.get():
                self.log("⏭️ Subida a GitHub omitida", "warning")
                return True
            
            carpeta = self.ruta_app.get()
            exe_path = os.path.join(carpeta, "dist", "RenombradorPDF.exe")
            
            if not os.path.exists(exe_path):
                self.log("❌ No se encontró el EXE", "error")
                return False
            
            self.log("📤 Subiendo a GitHub automáticamente...", "github")
            self.progreso.set(60)
            
            # Crear release y subir EXE
            self.log("📤 Subiendo EXE a GitHub Releases...", "github")
            tag = f"v{nueva_version}"
            
            check_cmd = ["gh", "release", "view", tag, "--repo", self.github_repo]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if check_result.returncode == 0:
                self.log(f"⚠️ Release {tag} ya existe, actualizando...", "warning")
                assets_cmd = ["gh", "release", "delete-asset", tag, "RenombradorPDF.exe", 
                             "--repo", self.github_repo, "--yes"]
                subprocess.run(assets_cmd, capture_output=True)
                upload_cmd = ["gh", "release", "upload", tag, exe_path, "--repo", self.github_repo, "--clobber"]
                subprocess.run(upload_cmd, check=True, capture_output=True)
                self.log(f"✅ EXE actualizado en release {tag}", "success")
            else:
                cmd = [
                    "gh", "release", "create",
                    tag,
                    exe_path,
                    "--repo", self.github_repo,
                    "--title", f"Versión {nueva_version}",
                    "--notes", self.mensaje_cambios.get() or f"Versión {nueva_version}",
                    "--latest"
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                self.log(f"✅ Release {tag} creado con EXE", "success")
            
            self.progreso.set(70)
            self.log("✅ ¡TODO SUBIDO A GITHUB AUTOMÁTICAMENTE! 🎉", "success")
            return True
            
        except Exception as e:
            self.log(f"❌ Error al subir: {e}", "error")
            return False
    
    def iniciar_proceso(self):
        if not self.ruta_app.get():
            messagebox.showerror("Error", "Selecciona la carpeta del proyecto")
            return
        if not self.nueva_version.get():
            messagebox.showerror("Error", "Ingresa la nueva versión")
            return
        
        self.build_btn.config(state="disabled")
        self.log("🚀 Iniciando Build & Deploy PRO...", "info")
        self.progreso.set(0)
        
        def thread_func():
            try:
                nueva_version = self.nueva_version.get()
                
                # ===== PASO 0: Sincronizar con GitHub (pull) =====
                self.log("🔄 Sincronizando con GitHub...", "github")
                self.git_sync()
                self.progreso.set(5)
                
                # 1. Instalar librerías
                if self.librerias_detectadas and self.auto_install_var.get():
                    self.log("🔧 Instalando librerías...", "info")
                    for lib in self.librerias_detectadas:
                        try:
                            subprocess.run([sys.executable, "-m", "pip", "install", lib], 
                                         check=True, capture_output=True)
                            self.log(f"✅ {lib} instalado", "success")
                        except:
                            self.log(f"⚠️ Error en {lib}", "warning")
                self.progreso.set(10)
                
                # 2. Actualizar versión en app.py y version.json
                self.log("📝 Actualizando versión en app.py y version.json...", "info")
                if not self.actualizar_version_en_codigo(nueva_version):
                    raise Exception("Error al actualizar versión")
                self.progreso.set(30)
                
                # 3. Compilar EXE
                self.log("📦 Compilando EXE...", "info")
                if not self.compilar_exe():
                    raise Exception("Error al compilar EXE")
                self.progreso.set(50)
                
                # 4. Crear instalador profesional
                self.log("📦 Creando instalador profesional...", "info")
                if not self.crear_instalador_profesional(nueva_version):
                    self.log("⚠️ Error al crear instalador", "warning")
                self.progreso.set(80)
                
                # ===== PASO 5: Subir cambios a GitHub (commit + push) =====
                if self.upload_var.get():
                    self.log("📤 Subiendo cambios a GitHub...", "github")
                    self.git_push_changes(nueva_version)
                    
                    # 6. Subir EXE a Releases
                    self.log("📤 Subiendo EXE a GitHub Releases...", "github")
                    self.subir_a_github_automatico(nueva_version)
                self.progreso.set(95)
                
                # Finalizar
                self.progreso.set(100)
                self.log("✅ ¡PROCESO COMPLETADO EXITOSAMENTE! 🎉", "success")
                self.log(f"📌 Nueva versión: {nueva_version}", "success")
                self.root.after(0, lambda: self.build_btn.config(state="normal"))
                
                messagebox.showinfo(
                    "✅ Éxito",
                    f"¡Build & Deploy PRO completado!\n\n"
                    f"📌 Versión: {nueva_version}\n"
                    f"📂 EXE: {self.ruta_app.get()}\\dist\\RenombradorPDF.exe\n"
                    f"📦 Instalador: {self.ruta_app.get()}\\Installer_PRO\\ICAMP_Setup_{nueva_version}.exe\n"
                    f"🔗 GitHub: https://github.com/{self.github_repo}/releases\n\n"
                    f"✅ app.py y version.json actualizados en GitHub\n"
                    f"🌐 Idiomas: {'Español, ' if self.idioma_es.get() else ''}{'Inglés' if self.idioma_en.get() else ''}"
                )
                
            except Exception as e:
                self.log(f"❌ Error: {e}", "error")
                self.root.after(0, lambda: self.build_btn.config(state="normal"))
                messagebox.showerror("Error", f"Error en el proceso:\n\n{str(e)}")
        
        threading.Thread(target=thread_func, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BuildDeployPro(root)
    root.mainloop()