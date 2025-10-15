import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import pandas as pd
import json
import webbrowser
import configparser
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path

# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================

class ClienteError(Exception):
    """
    Excepción base para todos los errores específicos del cliente.
    
    Esta clase actúa como la excepción padre de todas las excepciones
    personalizadas del sistema, permitiendo un manejo jerárquico de errores.
    Facilita el catch de cualquier error específico del cliente usando
    una sola clase base.
    
    Attributes:
        Hereda todos los atributos de Exception.
        
    Example:
        try:
            # Alguna operación del cliente
            pass
        except ClienteError as e:
            print(f"Error del cliente: {e}")
    """
    pass

class ConexionError(ClienteError):
    """
    Excepción específica para errores relacionados con conexiones de red.
    
    Se lanza cuando ocurren problemas durante:
    - Establecimiento de conexiones TCP/IP
    - Timeouts de conexión
    - Errores de resolución de nombres (DNS)
    - Conexiones rechazadas por el servidor
    - Pérdida de conexión durante la transmisión
    
    Inherits:
        ClienteError: Excepción base del cliente
        
    Example:
        raise ConexionError("No se pudo conectar al servidor 192.168.1.1:8080")
    """
    pass

class ArchivoError(ClienteError):
    """
    Excepción específica para errores de procesamiento de archivos.
    
    Se lanza cuando ocurren problemas durante:
    - Lectura de archivos Excel, CSV o TXT
    - Archivos corruptos o con formato inválido
    - Archivos vacíos o sin datos válidos
    - Conversión de datos a formato JSON
    - Validación de contenido de archivos
    
    Inherits:
        ClienteError: Excepción base del cliente
        
    Example:
        raise ArchivoError("El archivo CSV está corrupto en la línea 15")
    """
    pass

class ConfiguracionError(ClienteError):
    """
    Excepción específica para errores de configuración del sistema.
    
    Se lanza cuando ocurren problemas durante:
    - Carga de archivos de configuración (config.ini)
    - Guardado de configuraciones
    - Validación de parámetros de configuración
    - Valores de configuración inválidos (IP, puertos)
    - Permisos de archivo de configuración
    
    Inherits:
        ClienteError: Excepción base del cliente
        
    Example:
        raise ConfiguracionError("Puerto debe estar entre 1 y 65535")
    """
    pass

# =============================================================================
# CLASE BASE ABSTRACTA PARA CONEXIONES
# =============================================================================

class Conexion(ABC):
    """
    Clase base abstracta para manejar conexiones de red.
    
    Esta clase define la interfaz común para todos los tipos de conexiones
    de red en el sistema. Implementa el patrón Template Method, donde
    las subclases deben implementar los métodos abstractos específicos
    para cada tipo de conexión (TCP, UDP, etc.).
    
    Proporciona encapsulamiento para los datos de conexión (host, puerto)
    con validación automática, y mantiene el estado de la conexión.
    
    Attributes:
        _host (str): Dirección IP o nombre del servidor (privado)
        _puerto (int): Puerto de conexión (privado)
        _conectado (bool): Estado actual de la conexión (privado)
        
    Properties:
        host: Acceso controlado al host con validación
        puerto: Acceso controlado al puerto con validación  
        conectado: Solo lectura del estado de conexión
        
    Abstract Methods:
        conectar(): Debe establecer la conexión
        enviar_datos(): Debe enviar datos a través de la conexión
        desconectar(): Debe cerrar la conexión
        
    Example:
        # No se puede instanciar directamente (clase abstracta)
        # Se debe usar una subclase como ClienteSocket
        cliente = ClienteSocket("192.168.1.1", 8080)
        cliente.conectar()
        cliente.enviar_datos("Hola servidor")
        cliente.desconectar()
    """
    
    def __init__(self, host: str, puerto: int):
        """
        Inicializa una nueva instancia de conexión.
        
        Valida y establece los parámetros de conexión básicos.
        No establece la conexión real, solo prepara los datos.
        
        Args:
            host (str): Dirección IP o nombre del servidor de destino
            puerto (int): Puerto de conexión (1-65535)
            
        Raises:
            ConexionError: Si el host está vacío o el puerto es inválido
            
        Example:
            conexion = ClienteSocket("localhost", 8080)
        """
        self._host = self._validar_host(host)
        self._puerto = self._validar_puerto(puerto)
        self._conectado = False
    
    @property
    def host(self) -> str:
        """
        Obtiene la dirección del host de conexión.
        
        Property de solo lectura que devuelve la dirección IP o nombre
        del servidor configurado para la conexión.
        
        Returns:
            str: Dirección del host (IP o nombre)
            
        Example:
            print(f"Conectando a: {conexion.host}")
        """
        return self._host
    
    @host.setter
    def host(self, valor: str):
        """
        Establece una nueva dirección de host con validación.
        
        Valida que el host no esté vacío y lo almacena limpio
        (sin espacios en blanco al inicio o final).
        
        Args:
            valor (str): Nueva dirección de host
            
        Raises:
            ConexionError: Si el host está vacío o es inválido
            
        Example:
            conexion.host = "192.168.1.100"
        """
        self._host = self._validar_host(valor)
    
    @property
    def puerto(self) -> int:
        """
        Obtiene el puerto de conexión configurado.
        
        Returns:
            int: Número de puerto (1-65535)
            
        Example:
            print(f"Puerto configurado: {conexion.puerto}")
        """
        return self._puerto
    
    @puerto.setter
    def puerto(self, valor: int):
        """
        Establece un nuevo puerto de conexión con validación.
        
        Valida que el puerto esté en el rango válido (1-65535)
        antes de almacenarlo.
        
        Args:
            valor (int): Nuevo número de puerto
            
        Raises:
            ConexionError: Si el puerto está fuera del rango válido
            
        Example:
            conexion.puerto = 9090
        """
        self._puerto = self._validar_puerto(valor)
    
    @property
    def conectado(self) -> bool:
        """
        Indica si la conexión está actualmente establecida.
        
        Property de solo lectura que indica el estado actual
        de la conexión de red.
        
        Returns:
            bool: True si está conectado, False en caso contrario
            
        Example:
            if conexion.conectado:
                print("Conexión activa")
            else:
                print("Sin conexión")
        """
        return self._conectado
    
    def _validar_host(self, host: str) -> str:
        """
        Valida que el host sea una cadena no vacía.
        
        Método privado que verifica que el host proporcionado
        sea válido (no None, no vacío, no solo espacios).
        
        Args:
            host (str): Host a validar
            
        Returns:
            str: Host limpio (sin espacios extra)
            
        Raises:
            ConexionError: Si el host es inválido
            
        Note:
            Método privado, no debe ser llamado directamente
            desde fuera de la clase.
        """
        if not host or not host.strip():
            raise ConexionError("El host no puede estar vacío")
        return host.strip()
    
    def _validar_puerto(self, puerto: int) -> int:
        """
        Valida que el puerto esté en el rango permitido.
        
        Verifica que el puerto sea un entero y esté en el
        rango válido de puertos TCP/UDP (1-65535).
        
        Args:
            puerto (int): Puerto a validar
            
        Returns:
            int: Puerto validado
            
        Raises:
            ConexionError: Si el puerto es inválido
            
        Note:
            El puerto 0 está reservado y no se permite.
            Los puertos 1-1023 son privilegiados en sistemas Unix.
        """
        if not isinstance(puerto, int) or not (1 <= puerto <= 65535):
            raise ConexionError("El puerto debe ser un entero entre 1 y 65535")
        return puerto
    
    @abstractmethod
    def conectar(self) -> None:
        """
        Establece la conexión con el servidor remoto.
        
        Método abstracto que debe ser implementado por las subclases
        para establecer el tipo específico de conexión (TCP, UDP, etc.).
        
        Raises:
            ConexionError: Si no se puede establecer la conexión
            NotImplementedError: Si no está implementado en la subclase
            
        Note:
            Después de una conexión exitosa, la propiedad 'conectado'
            debe ser True.
        """
        pass
    
    @abstractmethod
    def enviar_datos(self, datos: Any) -> None:
        """
        Envía datos a través de la conexión establecida.
        
        Método abstracto que debe ser implementado por las subclases
        para enviar datos usando el protocolo específico de cada
        tipo de conexión.
        
        Args:
            datos (Any): Datos a enviar (el tipo depende de la implementación)
            
        Raises:
            ConexionError: Si hay errores durante el envío
            NotImplementedError: Si no está implementado en la subclase
            
        Note:
            La conexión debe estar establecida antes de llamar este método.
            Verificar la propiedad 'conectado' antes del envío.
        """
        pass
    
    @abstractmethod
    def desconectar(self) -> None:
        """
        Cierra la conexión de red establecida.
        
        Método abstracto que debe ser implementado por las subclases
        para cerrar ordenadamente la conexión y liberar recursos.
        
        Raises:
            NotImplementedError: Si no está implementado en la subclase
            
        Note:
            Después de desconectar, la propiedad 'conectado' debe ser False.
            Este método debe ser seguro de llamar múltiples veces.
        """
        pass

# =============================================================================
# CLASE PARA MANEJO DE ARCHIVOS
# =============================================================================

class ManejadorArchivos:
    """
    Clase para encapsular la lógica de lectura y procesamiento de archivos.
    
    Esta clase es responsable de manejar todos los aspectos relacionados
    con la carga, validación y procesamiento de archivos de datos.
    Soporta archivos Excel (.xlsx, .xls) y archivos de texto delimitado
    (.csv, .txt).
    
    Implementa el principio de responsabilidad única al centralizar
    todas las operaciones de archivos en una sola clase, proporcionando
    una interfaz limpia para el resto del sistema.
    
    Class Attributes:
        EXTENSIONES_EXCEL (set): Extensiones de archivos Excel soportadas
        EXTENSIONES_CSV (set): Extensiones de archivos CSV/TXT soportadas
        EXTENSIONES_PERMITIDAS (set): Todas las extensiones permitidas
        
    Attributes:
        _archivo_actual (Path): Ruta del archivo actualmente cargado (privado)
        _datos (DataFrame): Datos del archivo en formato pandas (privado)
        
    Properties:
        archivo_actual: Acceso de solo lectura al archivo actual
        tiene_datos: Indica si hay datos válidos cargados
        
    Example:
        manejador = ManejadorArchivos()
        datos = manejador.cargar_archivo("datos.xlsx")
        if manejador.tiene_datos:
            json_data = manejador.obtener_datos_json()
    """
    
    # Constantes de clase para extensiones soportadas
    EXTENSIONES_EXCEL = {'.xlsx', '.xls'}
    EXTENSIONES_CSV = {'.csv', '.txt'}
    EXTENSIONES_PERMITIDAS = EXTENSIONES_EXCEL | EXTENSIONES_CSV
    
    def __init__(self):
        """
        Inicializa una nueva instancia del manejador de archivos.
        
        Establece el estado inicial sin ningún archivo cargado.
        Todos los atributos se inicializan como None hasta que
        se cargue un archivo válido.
        
        Example:
            manejador = ManejadorArchivos()
            # manejador.tiene_datos será False inicialmente
        """
        self._archivo_actual: Optional[Path] = None
        self._datos: Optional[pd.DataFrame] = None
    
    @property
    def archivo_actual(self) -> Optional[Path]:
        """
        Obtiene la ruta del archivo actualmente cargado.
        
        Property de solo lectura que devuelve el objeto Path
        del archivo que está actualmente cargado en memoria.
        
        Returns:
            Optional[Path]: Ruta del archivo actual o None si no hay archivo
            
        Example:
            if manejador.archivo_actual:
                print(f"Archivo actual: {manejador.archivo_actual.name}")
            else:
                print("No hay archivo cargado")
        """
        return self._archivo_actual
    
    @property
    def tiene_datos(self) -> bool:
        """
        Verifica si hay datos válidos cargados en memoria.
        
        Comprueba que exista un DataFrame válido y que no esté vacío.
        Es útil para validar antes de realizar operaciones que
        requieren datos.
        
        Returns:
            bool: True si hay datos válidos, False en caso contrario
            
        Example:
            if manejador.tiene_datos:
                procesar_datos()
            else:
                print("Cargue un archivo primero")
        """
        return self._datos is not None and not self._datos.empty
    
    def cargar_archivo(self, ruta_archivo: str) -> pd.DataFrame:
        """
        Carga un archivo desde el sistema de archivos y lo procesa.
        
        Lee archivos Excel (.xlsx, .xls) o CSV/TXT (.csv, .txt) y los
        convierte en un DataFrame de pandas para su procesamiento.
        Realiza validaciones completas del archivo y su contenido.
        
        Args:
            ruta_archivo (str): Ruta completa al archivo a cargar
            
        Returns:
            pd.DataFrame: Datos del archivo en formato DataFrame
            
        Raises:
            ArchivoError: Si el archivo no existe, está corrupto, vacío,
                         o tiene un formato no soportado
                         
        Example:
            try:
                datos = manejador.cargar_archivo("/path/to/datos.xlsx")
                print(f"Cargadas {len(datos)} filas de datos")
            except ArchivoError as e:
                print(f"Error al cargar archivo: {e}")
                
        Note:
            Después de una carga exitosa, el archivo queda disponible
            a través de la propiedad 'archivo_actual' y los datos a
            través del método 'obtener_datos_json()'.
        """
        try:
            archivo_path = Path(ruta_archivo)
            
            # Validar existencia del archivo
            if not archivo_path.exists():
                raise ArchivoError(f"El archivo {ruta_archivo} no existe")
            
            # Validar extensión soportada
            if archivo_path.suffix.lower() not in self.EXTENSIONES_PERMITIDAS:
                raise ArchivoError(f"Formato de archivo no soportado: {archivo_path.suffix}")
            
            # Cargar según el tipo de archivo
            if archivo_path.suffix.lower() in self.EXTENSIONES_EXCEL:
                datos = pd.read_excel(archivo_path)
            else:  # CSV o TXT
                datos = pd.read_csv(archivo_path)
            
            # Validar que el archivo no esté vacío
            if datos.empty:
                raise ArchivoError("El archivo está vacío")
            
            # Guardar datos en la instancia
            self._archivo_actual = archivo_path
            self._datos = datos
            
            return datos
            
        except pd.errors.EmptyDataError:
            raise ArchivoError("El archivo está vacío o corrupto")
        except pd.errors.ParserError as e:
            raise ArchivoError(f"Error al parsear el archivo: {e}")
        except Exception as e:
            raise ArchivoError(f"Error inesperado al cargar el archivo: {e}")
    
    def obtener_datos_json(self) -> str:
        """
        Convierte los datos cargados a formato JSON.
        
        Transforma el DataFrame de pandas en una cadena JSON
        con formato de registros (lista de objetos JSON).
        Usa 'ensure_ascii=False' para mantener caracteres Unicode.
        
        Returns:
            str: Datos en formato JSON como cadena de texto
            
        Raises:
            ArchivoError: Si no hay datos cargados o hay error en la conversión
            
        Example:
            if manejador.tiene_datos:
                json_data = manejador.obtener_datos_json()
                print(f"JSON generado: {len(json_data)} caracteres")
                
        Note:
            El formato 'records' genera: [{"col1": val1, "col2": val2}, ...]
            que es ideal para transmisión a través de la red.
        """
        if not self.tiene_datos:
            raise ArchivoError("No hay datos cargados")
        
        try:
            return self._datos.to_json(orient='records', ensure_ascii=False)
        except Exception as e:
            raise ArchivoError(f"Error al convertir datos a JSON: {e}")
    
    def obtener_informacion_archivo(self) -> Dict[str, Any]:
        """
        Obtiene metadatos e información detallada del archivo actual.
        
        Recopila información útil sobre el archivo cargado incluyendo
        datos del sistema de archivos y estadísticas del contenido.
        
        Returns:
            Dict[str, Any]: Diccionario con información del archivo:
                - nombre: Nombre del archivo (sin ruta)
                - ruta: Ruta completa del archivo
                - extension: Extensión del archivo (.xlsx, .csv, etc.)
                - tamaño: Tamaño en bytes del archivo
                - filas: Número de filas de datos
                - columnas: Número de columnas de datos
                Si no hay archivo cargado, retorna diccionario vacío.
                
        Example:
            info = manejador.obtener_informacion_archivo()
            if info:
                print(f"Archivo: {info['nombre']}")
                print(f"Datos: {info['filas']} filas, {info['columnas']} columnas")
                print(f"Tamaño: {info['tamaño']} bytes")
                
        Note:
            El tamaño se obtiene del sistema de archivos, no del DataFrame.
            Las filas y columnas se obtienen del DataFrame cargado.
        """
        if not self._archivo_actual:
            return {}
        
        return {
            'nombre': self._archivo_actual.name,
            'ruta': str(self._archivo_actual),
            'extension': self._archivo_actual.suffix,
            'tamaño': self._archivo_actual.stat().st_size,
            'filas': len(self._datos) if self.tiene_datos else 0,
            'columnas': len(self._datos.columns) if self.tiene_datos else 0
        }

# =============================================================================
# CLASE PARA CONFIGURACIÓN
# =============================================================================

class ConfiguracionCliente:
    """
    Clase para manejar toda la configuración del cliente.
    
    Encapsula la lógica de gestión de configuración incluyendo
    carga, guardado y validación de parámetros de configuración.
    Utiliza ConfigParser para manejar archivos .ini de forma
    estándar y robusta.
    
    Esta clase implementa el principio de responsabilidad única
    al centralizar todo lo relacionado con configuración del sistema.
    Proporciona validación automática y valores por defecto seguros.
    
    Attributes:
        _archivo_config (str): Ruta del archivo de configuración (privado)
        _config (ConfigParser): Parser de configuración INI (privado)
        _ip_servidor (str): Dirección IP del servidor (privado)
        _puerto_servidor (int): Puerto del servidor (privado)
        
    Properties:
        ip_servidor: Acceso controlado a la IP del servidor
        puerto_servidor: Acceso controlado al puerto del servidor
        
    Default Values:
        IP del servidor: "127.0.0.1" (localhost)
        Puerto del servidor: 65432
        Archivo de configuración: "config.ini"
        
    Example:
        config = ConfiguracionCliente()
        config.ip_servidor = "192.168.1.100"
        config.puerto_servidor = 8080
        config.guardar_configuracion()
    """
    
    def __init__(self, archivo_config: str = "config.ini"):
        """
        Inicializa una nueva instancia de configuración del cliente.
        
        Establece valores por defecto seguros y carga la configuración
        existente desde el archivo especificado. Si el archivo no existe,
        se crearán los valores por defecto.
        
        Args:
            archivo_config (str): Nombre del archivo de configuración
                                 (por defecto "config.ini")
                                 
        Example:
            # Usar archivo por defecto
            config = ConfiguracionCliente()
            
            # Usar archivo personalizado
            config = ConfiguracionCliente("mi_config.ini")
        """
        self._archivo_config = archivo_config
        self._config = configparser.ConfigParser()
        self._ip_servidor = "127.0.0.1"  # Localhost por defecto
        self._puerto_servidor = 65432     # Puerto no privilegiado por defecto
        self.cargar_configuracion()
    
    @property
    def ip_servidor(self) -> str:
        """
        Obtiene la dirección IP del servidor configurada.
        
        Returns:
            str: Dirección IP del servidor (IPv4 o nombre de host)
            
        Example:
            print(f"Servidor configurado: {config.ip_servidor}")
        """
        return self._ip_servidor
    
    @ip_servidor.setter
    def ip_servidor(self, valor: str):
        """
        Establece una nueva dirección IP del servidor con validación.
        
        Valida que la IP no esté vacía y elimina espacios en blanco
        al inicio y final. No valida formato IP específico para
        permitir nombres de host.
        
        Args:
            valor (str): Nueva dirección IP o nombre de host
            
        Raises:
            ConfiguracionError: Si la IP está vacía o es None
            
        Example:
            config.ip_servidor = "192.168.1.100"
            config.ip_servidor = "servidor.empresa.com"
        """
        if not valor or not valor.strip():
            raise ConfiguracionError("La IP del servidor no puede estar vacía")
        self._ip_servidor = valor.strip()
    
    @property
    def puerto_servidor(self) -> int:
        """
        Obtiene el puerto del servidor configurado.
        
        Returns:
            int: Número de puerto (1-65535)
            
        Example:
            print(f"Puerto configurado: {config.puerto_servidor}")
        """
        return self._puerto_servidor
    
    @puerto_servidor.setter
    def puerto_servidor(self, valor: int):
        """
        Establece un nuevo puerto del servidor con validación.
        
        Valida que el puerto esté en el rango válido de puertos TCP/UDP.
        Permite tanto puertos privilegiados (1-1023) como no privilegiados.
        
        Args:
            valor (int): Nuevo número de puerto
            
        Raises:
            ConfiguracionError: Si el puerto está fuera del rango válido
            
        Example:
            config.puerto_servidor = 8080
            config.puerto_servidor = 443  # HTTPS
        """
        if not isinstance(valor, int) or not (1 <= valor <= 65535):
            raise ConfiguracionError("El puerto debe ser un entero entre 1 y 65535")
        self._puerto_servidor = valor
    
    def cargar_configuracion(self) -> None:
        """
        Carga la configuración desde el archivo INI especificado.
        
        Si el archivo no existe, crea uno nuevo con valores por defecto.
        Si existe, lee los valores de configuración y los valida.
        Maneja errores de formato y proporciona valores por defecto
        en caso de problemas.
        
        Raises:
            ConfiguracionError: Si hay errores al leer el archivo de configuración
            
        Example:
            config = ConfiguracionCliente()
            # La configuración se carga automáticamente en __init__
            
        Note:
            Este método se llama automáticamente durante la inicialización.
            También puede llamarse manualmente para recargar la configuración.
        """
        if not os.path.exists(self._archivo_config):
            self._crear_configuracion_por_defecto()
            return
        
        try:
            self._config.read(self._archivo_config)
            if 'SERVIDOR' in self._config:
                self._ip_servidor = self._config['SERVIDOR'].get('ip', self._ip_servidor)
                puerto_str = self._config['SERVIDOR'].get('puerto', str(self._puerto_servidor))
                self._puerto_servidor = int(puerto_str)
        except Exception as e:
            raise ConfiguracionError(f"Error al cargar la configuración: {e}")
    
    def guardar_configuracion(self) -> None:
        """
        Guarda la configuración actual en el archivo INI.
        
        Crea o actualiza el archivo de configuración con los valores
        actuales de IP y puerto del servidor. Crea la sección [SERVIDOR]
        si no existe.
        
        Raises:
            ConfiguracionError: Si hay errores al escribir el archivo
            
        Example:
            config.ip_servidor = "nueva.ip.com"
            config.puerto_servidor = 9000
            config.guardar_configuracion()  # Persiste los cambios
            
        Note:
            Los cambios en las propiedades no se guardan automáticamente.
            Debe llamar este método explícitamente para persistir cambios.
        """
        try:
            if 'SERVIDOR' not in self._config:
                self._config.add_section('SERVIDOR')
            
            self._config['SERVIDOR']['ip'] = self._ip_servidor
            self._config['SERVIDOR']['puerto'] = str(self._puerto_servidor)
            
            with open(self._archivo_config, 'w') as configfile:
                self._config.write(configfile)
        except Exception as e:
            raise ConfiguracionError(f"Error al guardar la configuración: {e}")
    
    def _crear_configuracion_por_defecto(self) -> None:
        """
        Crea un archivo de configuración con valores por defecto.
        
        Método privado que se llama cuando no existe el archivo
        de configuración. Crea un nuevo archivo con los valores
        por defecto del sistema.
        
        Raises:
            ConfiguracionError: Si no se puede crear el archivo por defecto
            
        Note:
            Este es un método privado que no debe llamarse directamente.
            Se invoca automáticamente desde cargar_configuracion().
        """
        try:
            self.guardar_configuracion()
        except Exception as e:
            raise ConfiguracionError(f"Error al crear configuración por defecto: {e}")
    
    def obtener_configuracion_completa(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración como un diccionario.
        
        Devuelve todos los parámetros de configuración en un formato
        estructurado que puede ser usado para logging, depuración
        o para mostrar al usuario.
        
        Returns:
            Dict[str, Any]: Diccionario con toda la configuración:
                - ip_servidor: IP del servidor configurada
                - puerto_servidor: Puerto del servidor configurado
                - archivo_config: Ruta del archivo de configuración
                
        Example:
            config_dict = config.obtener_configuracion_completa()
            print(f"Configuración actual: {config_dict}")
            
            for clave, valor in config_dict.items():
                print(f"{clave}: {valor}")
                
        Note:
            Útil para debugging y para mostrar información de configuración
            completa al usuario en ventanas de diagnóstico.
        """
        return {
            'ip_servidor': self._ip_servidor,
            'puerto_servidor': self._puerto_servidor,
            'archivo_config': self._archivo_config
        }

# =============================================================================
# IMPLEMENTACIÓN CONCRETA DE CONEXIÓN TCP
# =============================================================================

class ClienteSocket(Conexion):
    """
    Implementación concreta de conexión TCP que hereda de Conexion.
    
    Esta clase implementa el protocolo TCP para comunicación cliente-servidor.
    Proporciona conexión robusta con timeout configurable, manejo de errores
    específicos de TCP y soporte para context managers.
    
    Hereda de la clase abstracta Conexion e implementa todos los métodos
    abstractos requeridos. Añade funcionalidad específica de TCP como
    timeout de conexión y manejo de socket específico.
    
    Attributes:
        _socket (socket.socket): Socket TCP subyacente (privado)
        _timeout (int): Timeout de operaciones en segundos (privado)
        
    Properties:
        timeout: Acceso controlado al timeout de conexión
        
    Inherited Properties:
        host: Dirección del servidor (de Conexion)
        puerto: Puerto del servidor (de Conexion)
        conectado: Estado de la conexión (de Conexion)
        
    Example:
        # Uso básico
        cliente = ClienteSocket("192.168.1.1", 8080)
        cliente.conectar()
        cliente.enviar_datos("mensaje")
        cliente.desconectar()
        
        # Uso con context manager (recomendado)
        with ClienteSocket("localhost", 9000) as cliente:
            cliente.enviar_datos("datos importantes")
    """
    
    def __init__(self, host: str, puerto: int, timeout: int = 30):
        """
        Inicializa una nueva conexión TCP.
        
        Configura los parámetros básicos de conexión TCP incluyendo
        timeout personalizable. El timeout por defecto de 30 segundos
        es apropiado para la mayoría de aplicaciones de red.
        
        Args:
            host (str): Dirección IP o nombre del servidor
            puerto (int): Puerto TCP del servidor (1-65535)
            timeout (int): Timeout en segundos para operaciones (por defecto 30)
            
        Raises:
            ConexionError: Si los parámetros de conexión son inválidos
            
        Example:
            # Timeout por defecto (30 segundos)
            cliente = ClienteSocket("servidor.com", 8080)
            
            # Timeout personalizado para conexiones lentas
            cliente_lento = ClienteSocket("servidor-remoto.com", 8080, timeout=60)
        """
        super().__init__(host, puerto)
        self._socket: Optional[socket.socket] = None
        self._timeout = timeout
    
    @property
    def timeout(self) -> int:
        """
        Obtiene el timeout actual configurado para las operaciones.
        
        Returns:
            int: Timeout en segundos
            
        Example:
            print(f"Timeout configurado: {cliente.timeout} segundos")
        """
        return self._timeout
    
    @timeout.setter
    def timeout(self, valor: int):
        """
        Establece un nuevo timeout para las operaciones de red.
        
        El timeout se aplica a operaciones de conexión y envío de datos.
        Un timeout mayor permite conexiones más lentas pero puede hacer
        que la aplicación se cuelgue más tiempo en caso de problemas.
        
        Args:
            valor (int): Nuevo timeout en segundos (debe ser > 0)
            
        Raises:
            ConexionError: Si el timeout es menor o igual a 0
            
        Example:
            cliente.timeout = 60  # Para conexiones lentas
            cliente.timeout = 5   # Para conexiones rápidas locales
        """
        if valor <= 0:
            raise ConexionError("El timeout debe ser mayor que 0")
        self._timeout = valor
    
    def conectar(self) -> None:
        """
        Establece la conexión TCP con el servidor remoto.
        
        Implementación del método abstracto de la clase padre.
        Crea un socket TCP, configura el timeout y establece la conexión.
        Si ya existe una conexión activa, la cierra antes de crear una nueva.
        
        Maneja específicamente los errores más comunes de TCP:
        - Timeout de conexión
        - Error de resolución DNS
        - Conexión rechazada por el servidor
        - Otros errores de red
        
        Raises:
            ConexionError: Si no se puede establecer la conexión por cualquier motivo
            
        Example:
            cliente = ClienteSocket("localhost", 8080)
            try:
                cliente.conectar()
                print("Conexión establecida")
            except ConexionError as e:
                print(f"Error de conexión: {e}")
                
        Note:
            Después de una conexión exitosa, la propiedad 'conectado' será True.
            El socket queda configurado con el timeout especificado.
        """
        try:
            if self._conectado:
                self.desconectar()
            
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self._timeout)
            self._socket.connect((self._host, self._puerto))
            self._conectado = True
            
        except socket.timeout:
            raise ConexionError(f"Timeout al conectar con {self._host}:{self._puerto}")
        except socket.gaierror:
            raise ConexionError(f"No se pudo resolver el host: {self._host}")
        except ConnectionRefusedError:
            raise ConexionError(f"Conexión rechazada por {self._host}:{self._puerto}")
        except Exception as e:
            raise ConexionError(f"Error inesperado al conectar: {e}")
    
    def enviar_datos(self, datos: str) -> None:
        """
        Envía datos a través de la conexión TCP establecida.
        
        Implementación del método abstracto de la clase padre.
        Convierte los datos a bytes usando UTF-8 y los envía a través
        del socket TCP. Usa sendall() para garantizar que todos los
        datos se envíen completamente.
        
        Args:
            datos (str): Cadena de texto a enviar (se codifica en UTF-8)
            
        Raises:
            ConexionError: Si no hay conexión establecida, hay timeout,
                          o la conexión se pierde durante el envío
                          
        Example:
            cliente.conectar()
            try:
                cliente.enviar_datos("Hola servidor")
                cliente.enviar_datos('{"mensaje": "datos JSON"}')
            except ConexionError as e:
                print(f"Error al enviar: {e}")
                
        Note:
            La conexión debe estar establecida antes de llamar este método.
            Los datos se envían en codificación UTF-8 para soportar caracteres Unicode.
        """
        if not self._conectado or not self._socket:
            raise ConexionError("No hay conexión establecida")
        
        try:
            datos_bytes = datos.encode('utf-8')
            self._socket.sendall(datos_bytes)
        except socket.timeout:
            raise ConexionError("Timeout al enviar datos")
        except BrokenPipeError:
            raise ConexionError("La conexión se cerró inesperadamente")
        except Exception as e:
            raise ConexionError(f"Error al enviar datos: {e}")
    
    def desconectar(self) -> None:
        """
        Cierra la conexión TCP y libera recursos.
        
        Implementación del método abstracto de la clase padre.
        Cierra ordenadamente el socket TCP y actualiza el estado
        de conexión. Es seguro llamar este método múltiples veces.
        
        Example:
            cliente.conectar()
            # ... usar la conexión ...
            cliente.desconectar()  # Cierre explícito
            
        Note:
            Después de desconectar, la propiedad 'conectado' será False.
            Los errores durante el cierre se ignoran silenciosamente para
            evitar excepciones durante la limpieza de recursos.
        """
        if self._socket:
            try:
                self._socket.close()
            except:
                pass  # Ignorar errores al cerrar
            finally:
                self._socket = None
                self._conectado = False
    
    def __enter__(self):
        """
        Método de entrada para context manager.
        
        Permite usar la clase con la declaración 'with' para
        manejo automático de recursos. Establece la conexión
        automáticamente al entrar al bloque 'with'.
        
        Returns:
            ClienteSocket: La instancia actual para usar en el bloque with
            
        Example:
            with ClienteSocket("localhost", 8080) as cliente:
                cliente.enviar_datos("mensaje")
                # La conexión se cierra automáticamente al salir
        """
        self.conectar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Método de salida para context manager.
        
        Se llama automáticamente al salir del bloque 'with',
        incluso si ocurre una excepción. Garantiza que la
        conexión se cierre adecuadamente.
        
        Args:
            exc_type: Tipo de excepción (si ocurrió)
            exc_val: Valor de la excepción (si ocurrió)
            exc_tb: Traceback de la excepción (si ocurrió)
            
        Note:
            No suprime excepciones - si ocurre un error en el bloque 'with',
            se propagará después de cerrar la conexión.
        """
        self.desconectar()

# =============================================================================
# CLASES BASE PARA VENTANAS
# =============================================================================

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
    
    def __init__(self, parent: tk.Tk, titulo: str, tamaño: str = "400x300"):
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

# =============================================================================
# CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA
# =============================================================================

class ClienteGUI:
    """
    Clase principal de la interfaz gráfica del cliente.
    
    Esta es la clase controladora principal que coordina toda la aplicación.
    Implementa el patrón MVC como controlador, usando composición para
    integrar todas las funcionalidades del sistema.
    
    Responsabilidades:
    - Gestión de la interfaz gráfica principal
    - Coordinación entre componentes (archivos, configuración, red)
    - Manejo de eventos de usuario
    - Presentación de resultados y errores
    
    Usa composición para integrar:
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
        self.master.title("Cliente de Envío de Datos - Orientado a Objetos")
        self.master.geometry("450x250")
        self.master.resizable(True, False)
    
    def _crear_menu(self) -> None:
        """
        Crea la barra de menú principal de la aplicación.
        
        Configura menús para Configuración, Archivo y Ayuda con
        sus respectivos comandos y shortcuts.
        """
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Menú Configuración
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="Servidor...", command=self._mostrar_configuracion_servidor)
        
        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Abrir archivo...", command=self._seleccionar_archivo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.master.quit)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de...", command=self._mostrar_acerca_de)
    
    def _crear_interfaz(self) -> None:
        """Crea la interfaz principal"""
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
        """Crea la sección de selección de archivo"""
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
        """Crea la sección de información del archivo"""
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
        """Crea la sección de información de conexión"""
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
        """Crea el botón de envío"""
        self.send_button = ttk.Button(
            parent, 
            text="Enviar Datos al Servidor", 
            command=self._enviar_datos,
            state=tk.DISABLED
        )
        self.send_button.pack(fill='x', ipady=10)
    
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
        """Actualiza la información mostrada del archivo"""
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
        """Limpia la información del archivo actual"""
        self.file_label.config(text="Ningún archivo seleccionado")
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self._deshabilitar_envio()
    
    def _habilitar_envio(self) -> None:
        """Habilita el botón de envío"""
        self.send_button.config(state=tk.NORMAL)
    
    def _deshabilitar_envio(self) -> None:
        """Deshabilita el botón de envío"""
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
        """Muestra la ventana de configuración del servidor"""
        try:
            ventana_config = VentanaConfiguracion(self.master, self._configuracion)
            ventana_config.mostrar()
            
            # Actualizar etiqueta de conexión después de cerrar la ventana
            self.master.after(100, self._actualizar_etiqueta_conexion)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir configuración: {e}")
    
    def _actualizar_etiqueta_conexion(self) -> None:
        """Actualiza la etiqueta de información de conexión"""
        self.conexion_label.config(
            text=f"Servidor: {self._configuracion.ip_servidor}:{self._configuracion.puerto_servidor}"
        )
    
    def _mostrar_acerca_de(self) -> None:
        """Muestra la ventana 'Acerca de'"""
        try:
            ventana_acerca = VentanaAcercaDe(self.master)
            ventana_acerca.mostrar()
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana: {e}")

# =============================================================================
# FUNCIÓN PRINCIPAL Y PUNTO DE ENTRADA
# =============================================================================

def main():
    """
    Función principal de la aplicación.
    
    Punto de entrada que inicializa la aplicación Tkinter,
    crea la instancia principal de ClienteGUI e inicia el
    bucle de eventos de la interfaz gráfica.
    
    Maneja errores fatales durante la inicialización.
    
    Example:
        python cliente.py  # Ejecuta esta función
    """
    try:
        root = tk.Tk()
        app = ClienteGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error al inicializar la aplicación: {e}")

if __name__ == "__main__":
    main()