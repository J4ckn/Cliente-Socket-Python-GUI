import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import pandas as pd
import json
import webbrowser
import configparser
import os

class ClienteGUI:
   
    def __init__(self, master):
        self.master = master
        master.title("Cliente de Envío de Datos")
        master.geometry("400x200")

        self.filepath = None
        self.config_file = "config.ini"
        
        # Cargar configuración
        self.cargar_configuracion()

        # Crear barra de menú
        self.crear_menu()

        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill="both", expand=True)

        #seleccion de archivo
        file_frame = ttk.LabelFrame(main_frame, text="Selección de Archivo")
        file_frame.pack(fill=tk.X, pady=10)

        self.select_button = ttk.Button(file_frame, text="Cargar Archivo...", command=self.seleccionar_archivo)
        self.select_button.pack(pady=10)

        self.file_label = ttk.Label(file_frame, text="Ningún archivo seleccionado")
        self.file_label.pack(pady=5)

        #boton de envio
        self.send_button = ttk.Button(main_frame, text="Enviar Datos al Servidor", command=self.enviar_datos)
        # MODIFICACIÓN: Hacemos el botón más grande y visible
        self.send_button.pack(pady=10, fill='x', ipady=30)

    def crear_menu(self):
        """Crea la barra de menú de la aplicación"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Menú Configuración
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="Servidor...", command=self.mostrar_configuracion_servidor)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de...", command=self.mostrar_acerca_de)

    def cargar_configuracion(self):
        """Carga la configuración desde el archivo config.ini"""
        self.config = configparser.ConfigParser()
        
        # Valores por defecto
        self.ip_servidor = "127.0.0.1"
        self.puerto_servidor = "65432"
        
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                if 'SERVIDOR' in self.config:
                    self.ip_servidor = self.config['SERVIDOR'].get('ip', self.ip_servidor)
                    self.puerto_servidor = self.config['SERVIDOR'].get('puerto', self.puerto_servidor)
            except Exception as e:
                messagebox.showerror("Error de Configuración", 
                                   f"Error al cargar la configuración: {e}")

    def guardar_configuracion(self):
        """Guarda la configuración en el archivo config.ini"""
        try:
            if 'SERVIDOR' not in self.config:
                self.config.add_section('SERVIDOR')
            
            self.config['SERVIDOR']['ip'] = self.ip_servidor
            self.config['SERVIDOR']['puerto'] = self.puerto_servidor
            
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            messagebox.showerror("Error de Configuración", 
                               f"Error al guardar la configuración: {e}")

    def mostrar_configuracion_servidor(self):
        """Muestra la ventana de configuración del servidor"""
        # Crear ventana secundaria
        config_window = tk.Toplevel(self.master)
        config_window.title("Configuración del Servidor")
        config_window.geometry("350x150")
        config_window.resizable(False, False)
        
        # Centrar la ventana
        config_window.transient(self.master)
        config_window.grab_set()
        
        # Frame principal con padding
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Campos de configuración
        ttk.Label(main_frame, text="IP del Servidor:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ip_entry = ttk.Entry(main_frame, width=20)
        ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ip_entry.insert(0, self.ip_servidor)
        
        ttk.Label(main_frame, text="Puerto:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        port_entry = ttk.Entry(main_frame, width=20)
        port_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        port_entry.insert(0, self.puerto_servidor)
        
        # Configurar expansión de columnas
        main_frame.columnconfigure(1, weight=1)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        def guardar_y_cerrar():
            """Guarda la configuración y cierra la ventana"""
            try:
                # Validar puerto
                puerto_int = int(port_entry.get())
                if not (1 <= puerto_int <= 65535):
                    raise ValueError("Puerto debe estar entre 1 y 65535")
                
                # Guardar valores
                self.ip_servidor = ip_entry.get().strip()
                self.puerto_servidor = port_entry.get().strip()
                
                # Validar IP (básico)
                if not self.ip_servidor:
                    raise ValueError("La IP no puede estar vacía")
                
                # Guardar en archivo
                self.guardar_configuracion()
                
                messagebox.showinfo("Configuración", "Configuración guardada correctamente")
                config_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error de Validación", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")
        
        # Botones
        ttk.Button(button_frame, text="Guardar", command=guardar_y_cerrar).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancelar", command=config_window.destroy).pack(side=tk.LEFT)

    def mostrar_acerca_de(self):
        """Muestra la ventana de información 'Acerca de'"""
        # Crear ventana secundaria
        about_window = tk.Toplevel(self.master)
        about_window.title("Acerca de")
        about_window.resizable(False, False)
        
        # Centrar la ventana
        about_window.transient(self.master)
        about_window.grab_set()
        
        # Frame principal con padding
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Título del programa
        title_label = ttk.Label(main_frame, text="Cliente de Envío de Datos", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        
        # Descripción del programa (parte 1)
        description_text1 = """Aplicación cliente para envío de datos de deforestación a través de sockets TCP.
        
Permite seleccionar archivos en formato Excel o CSV y enviarlos a un servidor remoto para su procesamiento y almacenamiento en base de datos.

Librerías utilizadas:
• tkinter - Interfaz gráfica de usuario
• pandas - Procesamiento y lectura de archivos de datos
• socket - Comunicación TCP/IP
• json - Manejo de formato JSON
• webbrowser - Apertura de enlaces web

Proyecto universitario desarrollado como parte del estudio de comunicación cliente-servidor y programación con sockets en Python.

Este cliente funciona en conjunto con el servidor desarrollado por otro grupo de trabajo: """
        
        description_label1 = ttk.Label(main_frame, text=description_text1, 
                                     wraplength=450, justify="left")
        description_label1.pack(pady=(0, 5))
        
        # Frame para el repositorio del servidor (integrado en el texto)
        repo_frame = ttk.Frame(main_frame)
        repo_frame.pack(pady=(0, 10))
        
        # Link clickeable del repositorio (integrado)
        repo_link = tk.Text(repo_frame, height=1, width=60, wrap=tk.NONE, 
                           relief=tk.FLAT, bg=about_window.cget('bg'))
        repo_link.pack()
        
        repo_url = "https://github.com/EsotericHog/server_socket_python_gui"
        repo_link.insert(tk.END, repo_url)
        repo_link.tag_add("link", "1.0", "1.end")
        repo_link.tag_config("link", foreground="blue", underline=True)
        repo_link.config(state=tk.DISABLED, cursor="hand2")
        
        def abrir_repositorio(event):
            webbrowser.open(repo_url)
        
        repo_link.tag_bind("link", "<Button-1>", abrir_repositorio)
        
        # Separador
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=(0, 15))
        
        # Título de desarrolladores
        dev_title = ttk.Label(main_frame, text="Desarrollado por:", 
                             font=("Arial", 10, "bold"))
        dev_title.pack(pady=(0, 5))
        
        # Lista de integrantes (en orden alfabético y centrados)
        integrantes = [
            "Joaquín Calvillán",
            "Luciano Flores", 
            "Matías Polanco",
            "Maximiliano Prieto"
        ]
        
        for integrante in integrantes:
            integrante_label = ttk.Label(main_frame, text=f"• {integrante}")
            integrante_label.pack()
        
        # Botón de cerrar
        close_button = ttk.Button(main_frame, text="Cerrar", 
                                 command=about_window.destroy)
        close_button.pack(pady=(20, 0))
        
        # Ajustar el tamaño de la ventana dinámicamente
        about_window.update_idletasks()  # Asegurar que todos los widgets estén dibujados
        
        # Obtener el tamaño requerido del contenido
        req_width = main_frame.winfo_reqwidth() + 40  # +40 para padding extra
        req_height = main_frame.winfo_reqheight() + 40  # +40 para padding extra
        
        # Establecer un tamaño mínimo para la ventana
        min_width = 500
        min_height = 400
        
        # Usar el mayor entre el tamaño requerido y el mínimo
        final_width = max(req_width, min_width)
        final_height = max(req_height, min_height)
        
        # Aplicar el tamaño calculado
        about_window.geometry(f"{final_width}x{final_height}")
        
        # Centrar la ventana en la pantalla
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (final_width // 2)
        y = (about_window.winfo_screenheight() // 2) - (final_height // 2)
        about_window.geometry(f"{final_width}x{final_height}+{x}+{y}")

    def seleccionar_archivo(self):
      
        #tipos de archivo permitidos
        filetypes = (
            ('Archivos de Excel', '*.xlsx *.xls'),
            ('Archivos de texto plano', '*.csv *.txt'),
            ('Todos los archivos', '*.*')
        )
        filepath = filedialog.askopenfilename(title="Abrir archivo", filetypes=filetypes)
        if filepath:
            self.filepath = filepath
            #mostramos solo el nombre del archivo, no la ruta completa
            filename = filepath.split('/')[-1]
            self.file_label.config(text=filename)

    def enviar_datos(self):
       
        if not self.filepath:
            messagebox.showwarning("Archivo no seleccionado", "Por favor, cargue un archivo antes de enviarlo.")
            return

        try:
            #leer el archivo usando pandas
            if self.filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.filepath)
            elif self.filepath.endswith(('.csv', '.txt')):
                #se asume delimitador por coma, se puede adaptar
                df = pd.read_csv(self.filepath)
            else:
                messagebox.showerror("Formato no soportado", "El formato del archivo no es soportado.")
                return
            
            #convertir el dataFrame a formato JSON
            datos_json = df.to_json(orient='records')

            #conectar y enviar al servidor
            ip_servidor = self.ip_servidor
            puerto_servidor = int(self.puerto_servidor)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_servidor, puerto_servidor))
                #codificamos el string JSON a bytes para enviarlo
                s.sendall(datos_json.encode('utf-8'))
            
            messagebox.showinfo("Éxito", "Los datos han sido enviados correctamente al servidor.")

        except FileNotFoundError:
            messagebox.showerror("Error de Archivo", "El archivo seleccionado no se encontró.")
        except ConnectionRefusedError:
            messagebox.showerror("Error de Conexión", "No se pudo conectar al servidor. Compruebe que el servidor esté en ejecución y que la IP y el puerto sean correctos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteGUI(root)
    root.mainloop()