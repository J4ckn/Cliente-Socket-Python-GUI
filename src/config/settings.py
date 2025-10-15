"""
Módulo de configuración del cliente.

Este módulo maneja toda la configuración de la aplicación,
incluyendo carga, guardado y validación de parámetros.
"""

import configparser
import os
from typing import Dict, Any

from ..core.exceptions import ConfiguracionError


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