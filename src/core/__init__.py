"""
Módulo core del cliente.

Contiene componentes fundamentales como excepciones personalizadas
y clases base del sistema.
"""

from .exceptions import ClienteError, ConexionError, ArchivoError, ConfiguracionError

__all__ = ['ClienteError', 'ConexionError', 'ArchivoError', 'ConfiguracionError']