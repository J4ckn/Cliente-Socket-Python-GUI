"""
Módulo de conexiones de red.

Este módulo define las clases para manejar conexiones de red,
incluyendo la clase base abstracta y la implementación TCP concreta.
"""

import socket
from abc import ABC, abstractmethod
from typing import Any, Optional

from ..core.exceptions import ConexionError


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