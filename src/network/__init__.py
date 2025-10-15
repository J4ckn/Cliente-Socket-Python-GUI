"""
Módulo de red del cliente.

Contiene las clases responsables de la comunicación de red
y manejo de conexiones TCP/IP.
"""

from .connections import Conexion, ClienteSocket

__all__ = ['Conexion', 'ClienteSocket']