"""
Módulo de excepciones personalizadas del cliente.

Este módulo define todas las excepciones específicas del sistema,
proporcionando una jerarquía clara para el manejo de errores.
"""

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