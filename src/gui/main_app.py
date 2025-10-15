"""
Módulo principal de la interfaz gráfica del cliente.

Este módulo contiene la clase principal ClienteGUI que coordina
toda la aplicación de envío de datos, incluyendo la interfaz
de usuario y la lógica de negocio.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from pathlib import Path

from ..core.exceptions import ArchivoError, ConexionError
from ..config.settings import ConfiguracionCliente
from ..file_management.file_handler import ManejadorArchivos
from ..network.connections import ClienteSocket
from .windows import VentanaConfiguracion, VentanaAcercaDe


class ClienteGUI:
    """
    Clase principal de la interfaz gráfica del cliente.
    
    Esta clase coordina todos los componentes de la aplicación usando
    el patrón de composición. Gestiona la interfaz de usuario, maneja
    eventos y coordina la comunicación entre los diferentes módulos.
    
    Responsibilities:
    - Gestión de la interfaz gráfica principal
    - Coordinación entre módulos de configuración, archivos y red
    - Manejo de eventos de usuario
    - Control del flujo de trabajo de la aplicación
    
    Dependencies:
    - ConfiguracionCliente: Gestión de configuración
    - ManejadorArchivos: Procesamiento de archivos
    - ClienteSocket: Comunicación de red
    - VentanaConfiguracion/VentanaAcercaDe: Ventanas secundarias
    
    Attributes:
        master (tk.Tk): Ventana principal de tkinter
        _configuracion (ConfiguracionCliente): Gestor de configuración
        _manejador_archivos (ManejadorArchivos): Procesador de archivos
        _cliente_socket (ClienteSocket): Cliente de red (opcional)
        [widgets de interfaz]: Diversos widgets de tkinter
        
    Example:
        root = tk.Tk()
        app = ClienteGUI(root)
        root.mainloop()
    """
    
    def __init__(self, master: tk.Tk):
        """
        Inicializa la aplicación principal.
        
        Configura la ventana principal, inicializa todos los componentes
        necesarios usando composición y crea la interfaz gráfica completa.
        
        Args:
            master (tk.Tk): Ventana raíz de tkinter
            
        Example:
            root = tk.Tk()
            app = ClienteGUI(root)
        """
        self.master = master
        self._configurar_ventana_principal()
        
        # Inicializar componentes usando composición
        self._configuracion = ConfiguracionCliente()
        self._manejador_archivos = ManejadorArchivos()
        self._cliente_socket: Optional[ClienteSocket] = None
        
        # Crear interfaz
        self._crear_menu()
        self._crear_interfaz()
    
    def _configurar_ventana_principal(self) -> None:
        """
        Configura las propiedades básicas de la ventana principal.
        
        Establece título, tamaño y comportamiento de redimensionado
        de la ventana principal de la aplicación.
        """
        self.master.title("Cliente de Envío de Datos")
        self.master.geometry("450x360")
        self.master.resizable(True, False)
    
    def _crear_menu(self) -> None:
        """
        Crea la barra de menú principal de la aplicación.
        
        Configura menús para Configuración, Archivo y Ayuda con
        sus respectivos comandos y shortcuts.
        """
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Abrir archivo...", command=self._seleccionar_archivo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.master.quit)

        # Menú Configuración
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="Servidor...", command=self._mostrar_configuracion_servidor)
    
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de...", command=self._mostrar_acerca_de)
    
    def _crear_interfaz(self) -> None:
        """
        Crea la interfaz principal de la aplicación.
        
        Método privado que construye todos los elementos de la interfaz
        organizándolos en secciones lógicas mediante frames.
        """
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Frame de selección de archivo
        self._crear_seccion_archivo(main_frame)
        
        # Frame de información del archivo
        self._crear_seccion_informacion(main_frame)
        
        # Frame de conexión
        self._crear_seccion_conexion(main_frame)
        
        # Botón de envío
        self._crear_boton_envio(main_frame)
    
    def _crear_seccion_archivo(self, parent: ttk.Frame) -> None:
        """
        Crea la sección de selección de archivo en la interfaz.
        
        Args:
            parent (ttk.Frame): Frame padre donde se colocará la sección
        """
        file_frame = ttk.LabelFrame(parent, text="Selección de Archivo")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.select_button = ttk.Button(
            button_frame, 
            text="Seleccionar Archivo...", 
            command=self._seleccionar_archivo
        )
        self.select_button.pack(side=tk.LEFT)
        
        self.file_label = ttk.Label(button_frame, text="Ningún archivo seleccionado")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def _crear_seccion_informacion(self, parent: ttk.Frame) -> None:
        """
        Crea la sección de información del archivo en la interfaz.
        
        Args:
            parent (ttk.Frame): Frame padre donde se colocará la sección
        """
        info_frame = ttk.LabelFrame(parent, text="Información del Archivo")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(
            info_frame, 
            height=3, 
            state=tk.DISABLED,
            bg=self.master.cget('bg'),
            relief=tk.FLAT
        )
        self.info_text.pack(fill=tk.X, padx=10, pady=5)
    
    def _crear_seccion_conexion(self, parent: ttk.Frame) -> None:
        """
        Crea la sección de información de conexión en la interfaz.
        
        Args:
            parent (ttk.Frame): Frame padre donde se colocará la sección
        """
        conexion_frame = ttk.LabelFrame(parent, text="Configuración de Conexión")
        conexion_frame.pack(fill=tk.X, pady=(0, 10))
        
        config_info = ttk.Frame(conexion_frame)
        config_info.pack(fill=tk.X, padx=10, pady=5)
        
        self.conexion_label = ttk.Label(
            config_info, 
            text=f"Servidor: {self._configuracion.ip_servidor}:{self._configuracion.puerto_servidor}"
        )
        self.conexion_label.pack(side=tk.LEFT)
        
        ttk.Button(
            config_info, 
            text="Cambiar", 
            command=self._mostrar_configuracion_servidor
        ).pack(side=tk.RIGHT)
    
    def _crear_boton_envio(self, parent: ttk.Frame) -> None:
        """
        Crea el botón principal de envío de datos.
        
        Args:
            parent (ttk.Frame): Frame padre donde se colocará el botón
        """
        self.send_button = ttk.Button(
            parent, 
            text="Enviar Datos al Servidor", 
            command=self._enviar_datos,
            state=tk.DISABLED
        )
        self.send_button.pack(fill='x', ipady=10, pady=(10, 0))
    
    def _seleccionar_archivo(self) -> None:
        """
        Permite al usuario seleccionar un archivo de datos.
        
        Abre un diálogo de selección de archivos, carga el archivo
        seleccionado usando ManejadorArchivos y actualiza la interfaz
        con la información del archivo cargado.
        
        Maneja errores de carga y muestra mensajes apropiados.
        """
        filetypes = (
            ('Archivos de Excel', '*.xlsx *.xls'),
            ('Archivos CSV', '*.csv'),
            ('Archivos de texto', '*.txt'),
            ('Todos los archivos', '*.*')
        )
        
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de datos", 
            filetypes=filetypes
        )
        
        if filepath:
            try:
                # Cargar archivo usando el manejador
                self._manejador_archivos.cargar_archivo(filepath)
                
                # Actualizar interfaz
                self._actualizar_informacion_archivo()
                self._habilitar_envio()
                
                messagebox.showinfo(
                    "Archivo Cargado", 
                    f"Archivo '{Path(filepath).name}' cargado correctamente"
                )
                
            except ArchivoError as e:
                messagebox.showerror("Error de Archivo", str(e))
                self._limpiar_archivo()
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")
                self._limpiar_archivo()
    
    def _actualizar_informacion_archivo(self) -> None:
        """
        Actualiza la información mostrada del archivo cargado.
        
        Método privado que extrae información del ManejadorArchivos
        y actualiza los widgets de la interfaz con los detalles
        del archivo actualmente cargado.
        """
        if not self._manejador_archivos.archivo_actual:
            return
        
        info = self._manejador_archivos.obtener_informacion_archivo()
        
        # Actualizar etiqueta del archivo
        self.file_label.config(text=info['nombre'])
        
        # Actualizar información detallada
        info_texto = f"Archivo: {info['nombre']}\n"
        info_texto += f"Tipo: {info['extension'].upper()}\n"
        info_texto += f"Datos: {info['filas']} filas, {info['columnas']} columnas"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_texto)
        self.info_text.config(state=tk.DISABLED)
    
    def _limpiar_archivo(self) -> None:
        """
        Limpia la información del archivo actual de la interfaz.
        
        Resetea todos los widgets relacionados con el archivo a su
        estado inicial cuando no hay archivo seleccionado.
        """
        self.file_label.config(text="Ningún archivo seleccionado")
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self._deshabilitar_envio()
    
    def _habilitar_envio(self) -> None:
        """
        Habilita el botón de envío cuando hay datos válidos.
        """
        self.send_button.config(state=tk.NORMAL)
    
    def _deshabilitar_envio(self) -> None:
        """
        Deshabilita el botón de envío cuando no hay datos válidos.
        """
        self.send_button.config(state=tk.DISABLED)
    
    def _enviar_datos(self) -> None:
        """
        Envía los datos del archivo cargado al servidor.
        
        Coordina la conversión de datos a JSON, establecimiento de
        conexión TCP y envío de datos. Usa ClienteSocket con context
        manager para manejo automático de recursos.
        
        Maneja diferentes tipos de errores y muestra mensajes apropiados.
        """
        if not self._manejador_archivos.tiene_datos:
            messagebox.showerror("Error", "No hay datos para enviar")
            return
        
        try:
            # Obtener datos en formato JSON
            datos_json = self._manejador_archivos.obtener_datos_json()
            
            # Crear cliente socket y enviar datos
            with ClienteSocket(
                self._configuracion.ip_servidor, 
                self._configuracion.puerto_servidor
            ) as cliente:
                cliente.enviar_datos(datos_json)
            
            messagebox.showinfo(
                "Éxito", 
                "Los datos han sido enviados correctamente al servidor"
            )
            
        except ConexionError as e:
            messagebox.showerror("Error de Conexión", str(e))
        except ArchivoError as e:
            messagebox.showerror("Error de Archivo", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def _mostrar_configuracion_servidor(self) -> None:
        """
        Muestra la ventana modal de configuración del servidor.
        
        Crea y muestra una instancia de VentanaConfiguracion para
        permitir al usuario modificar la configuración de conexión.
        Actualiza la etiqueta de conexión después del cierre.
        """
        try:
            ventana_config = VentanaConfiguracion(self.master, self._configuracion)
            ventana_config.mostrar()
            
            # Actualizar etiqueta de conexión después de cerrar la ventana
            self.master.after(100, self._actualizar_etiqueta_conexion)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir configuración: {e}")
    
    def _actualizar_etiqueta_conexion(self) -> None:
        """
        Actualiza la etiqueta de información de conexión.
        
        Método privado que refresca la información mostrada sobre
        la configuración actual del servidor.
        """
        self.conexion_label.config(
            text=f"Servidor: {self._configuracion.ip_servidor}:{self._configuracion.puerto_servidor}"
        )
    
    def _mostrar_acerca_de(self) -> None:
        """
        Muestra la ventana modal 'Acerca de' con información del proyecto.
        
        Crea y muestra una instancia de VentanaAcercaDe con información
        detallada sobre la aplicación, desarrolladores y características.
        """
        try:
            ventana_acerca = VentanaAcercaDe(self.master)
            ventana_acerca.mostrar()
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana: {e}")