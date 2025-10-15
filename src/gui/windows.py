"""
Módulo de ventanas de la interfaz gráfica.

Este módulo contiene todas las clases de ventanas secundarias
de la aplicación, incluyendo la clase base abstracta.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from abc import ABC, abstractmethod

from ..core.exceptions import ConfiguracionError
from ..config.settings import ConfiguracionCliente


class VentanaBase(ABC):
    """
    Clase base abstracta para ventanas secundarias de la aplicación.
    
    Proporciona funcionalidad común para todas las ventanas secundarias
    (modales) del sistema. Implementa el patrón Template Method donde
    las subclases deben implementar el contenido específico.
    
    Maneja automáticamente:
    - Configuración básica de ventana (modal, transient)
    - Centrado en pantalla
    - Configuración de tamaño
    - Bloqueo de interacción con ventana padre
    
    Attributes:
        parent (tk.Tk): Ventana padre
        ventana (tk.Toplevel): Ventana actual
        
    Abstract Methods:
        _crear_contenido(): Debe implementar el contenido específico
        
    Example:
        class MiVentana(VentanaBase):
            def _crear_contenido(self):
                ttk.Label(self.ventana, text="Mi contenido").pack()
        
        ventana = MiVentana(root, "Mi Título", "300x200")
        ventana.mostrar()
    """
    
    def __init__(self, parent: tk.Tk, titulo: str, tamaño: str = "400x400"):
        """
        Inicializa una nueva ventana secundaria.
        
        Configura la ventana con propiedades comunes y llama a los
        métodos de configuración y creación de contenido.
        
        Args:
            parent (tk.Tk): Ventana padre de la aplicación
            titulo (str): Título de la ventana
            tamaño (str): Tamaño en formato "ancho x alto" (ej: "400x300")
            
        Example:
            ventana = MiVentana(ventana_principal, "Configuración", "350x200")
        """
        self.parent = parent
        self.ventana = tk.Toplevel(parent)
        self.ventana.title(titulo)
        self.ventana.geometry(tamaño)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self.ventana.grab_set()
        self._configurar_ventana()
        self._crear_contenido()
    
    @abstractmethod
    def _crear_contenido(self) -> None:
        """
        Método abstracto para crear el contenido específico de la ventana.
        
        Las subclases deben implementar este método para definir
        los widgets y el layout específico de cada tipo de ventana.
        
        Raises:
            NotImplementedError: Si no está implementado en la subclase
        """
        pass
    
    def _configurar_ventana(self) -> None:
        """
        Configuración común aplicada a todas las ventanas secundarias.
        
        Centra la ventana en la pantalla basándose en el tamaño configurado.
        Método privado llamado automáticamente durante la inicialización.
        """
        # Centrar la ventana
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - (int(self.ventana.geometry().split('x')[0]) // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (int(self.ventana.geometry().split('+')[0].split('x')[1]) // 2)
        self.ventana.geometry(f"+{x}+{y}")
    
    def mostrar(self) -> None:
        """
        Hace visible la ventana y le da el foco.
        
        Método público para mostrar la ventana al usuario y establecer
        el foco en ella para interacción inmediata.
        """
        self.ventana.focus_set()
    
    def cerrar(self) -> None:
        """
        Cierra y destruye la ventana.
        
        Método público para cerrar la ventana y liberar sus recursos.
        Equivale a hacer clic en el botón X de la ventana.
        """
        self.ventana.destroy()


class VentanaConfiguracion(VentanaBase):
    """
    Ventana modal para configuración del servidor.
    
    Permite al usuario modificar la configuración de conexión
    (IP y puerto del servidor) con validación en tiempo real.
    Hereda de VentanaBase para funcionalidad común de ventanas.
    
    Attributes:
        configuracion (ConfiguracionCliente): Instancia de configuración a modificar
        ip_entry (ttk.Entry): Campo de entrada para IP
        puerto_entry (ttk.Entry): Campo de entrada para puerto
    """
    
    def __init__(self, parent: tk.Tk, configuracion: ConfiguracionCliente):
        """
        Inicializa la ventana de configuración.
        
        Args:
            parent (tk.Tk): Ventana padre
            configuracion (ConfiguracionCliente): Configuración a editar
        """
        self.configuracion = configuracion
        super().__init__(parent, "Configuración del Servidor", "350x180")
    
    def _crear_contenido(self) -> None:
        """
        Crea el formulario de configuración del servidor.
        
        Implementa el método abstracto de VentanaBase para crear
        campos de entrada de IP y puerto con botones de acción.
        """
        main_frame = ttk.Frame(self.ventana, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Campo IP
        ttk.Label(main_frame, text="IP del Servidor:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_entry = ttk.Entry(main_frame, width=20)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.ip_entry.insert(0, self.configuracion.ip_servidor)
        
        # Campo Puerto
        ttk.Label(main_frame, text="Puerto:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.puerto_entry = ttk.Entry(main_frame, width=20)
        self.puerto_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.puerto_entry.insert(0, str(self.configuracion.puerto_servidor))
        
        main_frame.columnconfigure(1, weight=1)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="Guardar", command=self._guardar_configuracion).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancelar", command=self.cerrar).pack(side=tk.LEFT)
    
    def _guardar_configuracion(self) -> None:
        """
        Valida y guarda la configuración ingresada por el usuario.
        
        Método privado que maneja la validación de datos del formulario,
        actualiza la configuración y la persiste al archivo. Muestra
        mensajes de error o éxito según corresponda.
        
        Raises:
            Maneja internamente las excepciones y muestra messageboxes
        """
        try:
            # Validar y guardar
            ip = self.ip_entry.get().strip()
            puerto = int(self.puerto_entry.get().strip())
            
            self.configuracion.ip_servidor = ip
            self.configuracion.puerto_servidor = puerto
            self.configuracion.guardar_configuracion()
            
            messagebox.showinfo("Configuración", "Configuración guardada correctamente")
            self.cerrar()
            
        except ValueError:
            messagebox.showerror("Error de Validación", "El puerto debe ser un número válido")
        except ConfiguracionError as e:
            messagebox.showerror("Error de Configuración", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")


class VentanaAcercaDe(VentanaBase):
    """
    Ventana modal que muestra información sobre la aplicación.
    
    Presenta información sobre el proyecto, librerías utilizadas,
    desarrolladores y enlaces de referencia. Hereda de VentanaBase
    para funcionalidad común de ventanas modales.
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializa la ventana 'Acerca de'.
        
        Args:
            parent (tk.Tk): Ventana padre de la aplicación
        """
        super().__init__(parent, "Acerca de", "500x600")
    
    def _crear_contenido(self) -> None:
        """
        Crea el contenido informativo de la ventana.
        
        Implementa el método abstracto de VentanaBase para mostrar
        información detallada sobre la aplicación, desarrolladores
        y características técnicas.
        """
        main_frame = ttk.Frame(self.ventana, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Cliente de Envío de Datos", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Descripción
        description_text = """Aplicación cliente para envío de datos de deforestación a través de sockets TCP.

Permite seleccionar archivos en formato Excel o CSV y enviarlos a un servidor remoto para su procesamiento y almacenamiento en base de datos.

Características de la aplicación:
• Arquitectura orientada a objetos con encapsulamiento
• Herencia y composición de clases
• Manejo robusto de excepciones
• Interfaz gráfica intuitiva
• Configuración persistente
• Estructura modular con separación de responsabilidades

Librerías utilizadas:
• tkinter - Interfaz gráfica de usuario
• pandas - Procesamiento y lectura de archivos de datos
• socket - Comunicación TCP/IP
• json - Manejo de formato JSON
• webbrowser - Apertura de enlaces web
• configparser - Gestión de configuración

Proyecto universitario desarrollado como parte del estudio de comunicación cliente-servidor y programación con sockets en Python.

Este cliente funciona en conjunto con el servidor desarrollado por otro grupo de trabajo:"""
        
        description_label = ttk.Label(main_frame, text=description_text, 
                                     wraplength=450, justify="left")
        description_label.pack(pady=(0, 5))
        
        # Repositorio
        repo_frame = ttk.Frame(main_frame)
        repo_frame.pack(pady=(0, 10))
        
        repo_link = tk.Text(repo_frame, height=1, width=60, wrap=tk.NONE, 
                           relief=tk.FLAT, bg=self.ventana.cget('bg'))
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
        
        # Desarrolladores
        dev_title = ttk.Label(main_frame, text="Desarrollado por:", 
                             font=("Arial", 10, "bold"))
        dev_title.pack(pady=(0, 5))
        
        integrantes = [
            "Joaquín Calvillán",
            "Luciano Flores", 
            "Matías Polanco",
            "Maximiliano Prieto"
        ]
        
        for integrante in integrantes:
            integrante_label = ttk.Label(main_frame, text=f"• {integrante}")
            integrante_label.pack()
        
        # Botón cerrar
        close_button = ttk.Button(main_frame, text="Cerrar", command=self.cerrar)
        close_button.pack(pady=(20, 0))