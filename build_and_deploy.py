"""
BUILD & DEPLOY AUTOMÁTICO PARA ICAMP
-----------------------------------
HACE TODO AUTOMÁTICAMENTE:
1. Actualiza app.py con nueva versión
2. Crea version.json
3. Sube app.py y version.json a GitHub
4. Compila EXE con icono e imágenes
5. Sube EXE a GitHub Releases
6. Crea instalador (opcional)

USO: python build_and_deploy.py
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
import time

class BuildDeployApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Build & Deploy - ICAMP")
        self.root.geometry("850x700")
        self.root.resizable(True, True)
        
        # ===== CONFIGURACIÓN =====
        self.github_repo = "Mrsys-creator/ICAMP"
        self.github_token = ""  # Dejar vacío, usará gh CLI
        
        # Variables
        self.ruta_app = tk.StringVar()
        self.nueva_version = tk.StringVar()
        self.mensaje_cambios = tk.StringVar()
        self.progreso = tk.DoubleVar()
        
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
        
        titulo = ttk.Label(main_frame, text="🚀 BUILD & DEPLOY - ICAMP", font=("Arial", 16, "bold"))
        titulo.pack(pady=10)
        
        if self.es_python_314:
            warn_frame = ttk.Frame(main_frame, relief="solid", borderwidth=2)
            warn_frame.pack(fill="x", pady=5)
            ttk.Label(warn_frame, text="⚠️ PYTHON 3.14 - Usando Python 3.13 para compilar", 
                     foreground="orange", font=("Arial", 11)).pack(pady=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="📊 Información", padding="10")
        info_frame.pack(fill="x", pady=5)
        ttk.Label(info_frame, text=f"📂 Versión actual: {self.version_actual}").pack(anchor="w")
        ttk.Label(info_frame, text=f"📁 Repositorio: {self.github_repo}").pack(anchor="w")
        ttk.Label(info_frame, text=f"📌 Usando gh CLI para subir a GitHub").pack(anchor="w")
        
        # Carpeta
        ttk.Label(main_frame, text="📁 Carpeta del proyecto:").pack(anchor="w", pady=(10, 0))
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill="x", pady=5)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.ruta_app, width=50)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="📂 Buscar", command=self.seleccionar_carpeta).pack(side="right")
        
        # Versión
        ttk.Label(main_frame, text="🔢 Nueva versión (ej: 1.0.6):").pack(anchor="w", pady=(10, 0))
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill="x", pady=5)
        self.version_entry = ttk.Entry(version_frame, textvariable=self.nueva_version, width=25)
        self.version_entry.pack(side="left")
        ttk.Label(version_frame, text=f"  Actual: {self.version_actual}", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        # Mensaje de cambios
        ttk.Label(main_frame, text="📝 Mensaje de cambios (se mostrará en GitHub):").pack(anchor="w", pady=(10, 0))
        self.mensaje_entry = ttk.Entry(main_frame, textvariable=self.mensaje_cambios, width=70)
        self.mensaje_entry.pack(fill="x", pady=5)
        self.mensaje_entry.insert(0, "Nueva versión con mejoras")
        
        # Botón detectar librerías
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="🔍 Detectar librerías", command=self.detectar_librerias).pack(side="left", padx=5)
        self.librerias_label = ttk.Label(btn_frame, text="", font=("Arial", 9))
        self.librerias_label.pack(side="left", padx=10)
        
        # Opciones
        opciones_frame = ttk.LabelFrame(main_frame, text="⚙️ Opciones", padding="10")
        opciones_frame.pack(fill="x", pady=10)
        self.upload_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="📤 Subir a GitHub (EXE + app.py + version.json)", 
                       variable=self.upload_var).pack(anchor="w")
        self.installer_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opciones_frame, text="📦 Crear instalador (Inno Setup)", 
                       variable=self.installer_var).pack(anchor="w")
        self.auto_install_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="🔧 Instalar librerías automáticamente", 
                       variable=self.auto_install_var).pack(anchor="w")
        
        # Progreso
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progreso, maximum=100, length=600)
        self.progress_bar.pack(fill="x", pady=10)
        self.status_label = ttk.Label(main_frame, text="✅ Listo", font=("Arial", 10))
        self.status_label.pack(anchor="w", pady=5)
        
        # Botones
        btn_accion = ttk.Frame(main_frame)
        btn_accion.pack(fill="x", pady=10)
        self.build_btn = ttk.Button(btn_accion, text="🚀 INICIAR BUILD & DEPLOY", 
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
                "requests": "requests",
                "beautifulsoup4": "beautifulsoup4"
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
    
    def actualizar_version_en_codigo(self, nueva_version):
        try:
            ruta = os.path.join(self.ruta_app.get(), "app.py")
            with open(ruta, "r", encoding="utf-8") as f:
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
            
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            
            self.log(f"✅ Versión actualizada a {nueva_version} en app.py", "success")
            return True
        except Exception as e:
            self.log(f"❌ Error: {e}", "error")
            return False
    
    def crear_version_json(self, nueva_version):
        try:
            carpeta = self.ruta_app.get()
            version_json = {
                "version": nueva_version,
                "mensaje": self.mensaje_cambios.get() or f"Versión {nueva_version}",
                "url_descarga": f"https://github.com/{self.github_repo}/releases/download/v{nueva_version}/RenombradorPDF.exe",
                "url_app": f"https://raw.githubusercontent.com/{self.github_repo}/main/app.py",
                "nuevas_librerias": self.librerias_detectadas,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            ruta_json = os.path.join(carpeta, "version.json")
            with open(ruta_json, "w", encoding="utf-8") as f:
                json.dump(version_json, f, indent=4, ensure_ascii=False)
            
            self.log("✅ version.json creado", "success")
            return True
        except Exception as e:
            self.log(f"❌ Error al crear version.json: {e}", "error")
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
            
            self.log("📤 Subiendo TODO a GitHub automáticamente...", "github")
            self.progreso.set(60)
            
            # ===== PASO 1: Subir app.py y version.json =====
            self.log("📤 1. Subiendo app.py y version.json...", "github")
            try:
                # Inicializar git si no existe
                if not os.path.exists(os.path.join(carpeta, ".git")):
                    self.log("📌 Inicializando repositorio git...", "info")
                    subprocess.run(["git", "init"], cwd=carpeta, check=True, capture_output=True)
                    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{self.github_repo}.git"], 
                                 cwd=carpeta, check=True, capture_output=True)
                    subprocess.run(["git", "branch", "-M", "main"], cwd=carpeta, check=True, capture_output=True)
                
                # Agregar archivos
                subprocess.run(["git", "add", "app.py", "version.json"], cwd=carpeta, check=True, capture_output=True)
                
                # Commit
                commit_msg = f"Actualizar a versión {nueva_version}: {self.mensaje_cambios.get() or 'Nueva versión'}"
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=carpeta, check=True, capture_output=True)
                
                # Push
                self.log("📤 Haciendo push a GitHub...", "github")
                subprocess.run(["git", "push", "-u", "origin", "main"], cwd=carpeta, check=True, capture_output=True)
                self.log("✅ app.py y version.json actualizados en GitHub", "success")
                
            except subprocess.CalledProcessError as e:
                if "nothing to commit" in str(e.stderr):
                    self.log("ℹ️ No hay cambios para commitear", "info")
                else:
                    self.log(f"⚠️ Error en git: {e}", "warning")
            
            # ===== PASO 2: Crear release y subir EXE =====
            self.log("📤 2. Subiendo EXE a GitHub Releases...", "github")
            tag = f"v{nueva_version}"
            
            # Verificar si el release ya existe
            check_cmd = ["gh", "release", "view", tag, "--repo", self.github_repo]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if check_result.returncode == 0:
                # El release ya existe, actualizar
                self.log(f"⚠️ Release {tag} ya existe, actualizando...", "warning")
                # Eliminar assets existentes
                assets_cmd = ["gh", "release", "delete-asset", tag, "RenombradorPDF.exe", 
                             "--repo", self.github_repo, "--yes"]
                subprocess.run(assets_cmd, capture_output=True)
                # Subir nuevo EXE
                upload_cmd = ["gh", "release", "upload", tag, exe_path, "--repo", self.github_repo, "--clobber"]
                subprocess.run(upload_cmd, check=True, capture_output=True)
                self.log(f"✅ EXE actualizado en release {tag}", "success")
            else:
                # Crear nuevo release
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
            
            self.progreso.set(80)
            self.log("✅ ¡TODO SUBIDO A GITHUB AUTOMÁTICAMENTE! 🎉", "success")
            return True
            
        except Exception as e:
            self.log(f"❌ Error al subir: {e}", "error")
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
            
            # Instalar PyInstaller si es necesario
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
    
    def crear_instalador(self):
        try:
            if not self.installer_var.get():
                return True
            
            self.log("📦 Creando instalador...", "info")
            
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
                return False
            
            carpeta = self.ruta_app.get()
            exe_path = os.path.join(carpeta, "dist", "RenombradorPDF.exe")
            nueva_version = self.nueva_version.get()
            
            iss_content = f'''
[Setup]
AppName=ICAMP
AppVersion={nueva_version}
DefaultDirName={{pf}}\\ICAMP
DefaultGroupName=ICAMP
UninstallDisplayIcon={{app}}\\RenombradorPDF.exe
Compression=lzma2
SolidCompression=yes
OutputDir={carpeta}\\Installer
OutputBaseFilename=ICAMP_Setup_{nueva_version}

[Files]
Source: "{exe_path}"; DestDir: "{{app}}"

[Icons]
Name: "{{group}}\\ICAMP"; Filename: "{{app}}\\RenombradorPDF.exe"
Name: "{{commondesktop}}\\ICAMP"; Filename: "{{app}}\\RenombradorPDF.exe"

[Run]
Filename: "{{app}}\\RenombradorPDF.exe"; Description: "Iniciar ICAMP"; Flags: postinstall nowait
'''
            
            iss_path = os.path.join(carpeta, "installer.iss")
            with open(iss_path, "w", encoding="utf-8") as f:
                f.write(iss_content)
            
            subprocess.run([inno_exe, iss_path], check=True, capture_output=True)
            self.log("✅ Instalador creado", "success")
            return True
            
        except Exception as e:
            self.log(f"⚠️ Error: {e}", "warning")
            return False
    
    def iniciar_proceso(self):
        if not self.ruta_app.get():
            messagebox.showerror("Error", "Selecciona la carpeta del proyecto")
            return
        if not self.nueva_version.get():
            messagebox.showerror("Error", "Ingresa la nueva versión")
            return
        
        # Verificar gh CLI
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except:
            respuesta = messagebox.askyesno(
                "⚠️ GitHub CLI no instalado",
                "El script necesita gh CLI para subir automáticamente a GitHub.\n\n"
                "¿Quieres continuar? (la subida a GitHub fallará)"
            )
            if not respuesta:
                return
        
        self.build_btn.config(state="disabled")
        self.log("🚀 Iniciando proceso de Build & Deploy...", "info")
        self.progreso.set(0)
        
        def thread_func():
            try:
                nueva_version = self.nueva_version.get()
                
                # 1. Instalar librerías
                if self.librerias_detectadas and self.auto_install_var.get():
                    self.log("🔧 Instalando librerías detectadas...", "info")
                    for lib in self.librerias_detectadas:
                        try:
                            subprocess.run([sys.executable, "-m", "pip", "install", lib], 
                                         check=True, capture_output=True)
                            self.log(f"✅ {lib} instalado", "success")
                        except Exception as e:
                            self.log(f"⚠️ Error en {lib}: {e}", "warning")
                self.progreso.set(10)
                
                # 2. Actualizar versión en código
                self.log("📝 Actualizando versión en código...", "info")
                if not self.actualizar_version_en_codigo(nueva_version):
                    raise Exception("Error al actualizar versión")
                self.progreso.set(20)
                
                # 3. Crear version.json
                self.log("📝 Creando version.json...", "info")
                if not self.crear_version_json(nueva_version):
                    raise Exception("Error al crear version.json")
                self.progreso.set(30)
                
                # 4. Compilar EXE
                self.log("📦 Compilando EXE...", "info")
                if not self.compilar_exe():
                    raise Exception("Error al compilar EXE")
                self.progreso.set(60)
                
                # 5. Subir a GitHub (TODO automático)
                if self.upload_var.get():
                    self.log("📤 Subiendo a GitHub automáticamente...", "github")
                    if not self.subir_a_github_automatico(nueva_version):
                        self.log("⚠️ Error en subida a GitHub, continuando...", "warning")
                self.progreso.set(85)
                
                # 6. Crear instalador (opcional)
                if self.installer_var.get():
                    self.log("📦 Creando instalador...", "info")
                    self.crear_instalador()
                
                self.progreso.set(100)
                self.log("✅ ¡PROCESO COMPLETADO EXITOSAMENTE! 🎉", "success")
                self.log(f"📌 Nueva versión: {nueva_version}", "success")
                self.log(f"📂 EXE: {self.ruta_app.get()}\\dist\\RenombradorPDF.exe", "success")
                self.log(f"🔗 GitHub: https://github.com/{self.github_repo}/releases", "success")
                self.root.after(0, lambda: self.build_btn.config(state="normal"))
                
                messagebox.showinfo(
                    "✅ Éxito",
                    f"¡Build & Deploy completado!\n\n"
                    f"📌 Versión: {nueva_version}\n"
                    f"📂 EXE: {self.ruta_app.get()}\\dist\\RenombradorPDF.exe\n"
                    f"🔗 GitHub: https://github.com/{self.github_repo}/releases\n\n"
                    f"📦 Librerías: {', '.join(self.librerias_detectadas) if self.librerias_detectadas else 'Ninguna'}\n\n"
                    f"✅ app.py y version.json actualizados en GitHub\n"
                    f"✅ EXE subido a GitHub Releases"
                )
                
            except Exception as e:
                self.log(f"❌ Error: {e}", "error")
                self.root.after(0, lambda: self.build_btn.config(state="normal"))
                messagebox.showerror("Error", f"Error en el proceso:\n\n{str(e)}")
        
        threading.Thread(target=thread_func, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BuildDeployApp(root)
    root.mainloop()