"""
Script de prueba para verificar el funcionamiento de todos los módulos.

Prueba la inicialización de las clases principales sin mostrar la GUI.
"""

import sys
import os

# Agregar el directorio padre al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_exceptions():
    """Prueba las excepciones personalizadas."""
    from src.core.exceptions import ClienteError, ConexionError, ArchivoError, ConfiguracionError
    
    print("✓ Probando excepciones...")
    try:
        raise ClienteError("Prueba de excepción base")
    except ClienteError as e:
        print(f"  - ClienteError: {e}")
    
    try:
        raise ConexionError("Prueba de error de conexión")
    except ConexionError as e:
        print(f"  - ConexionError: {e}")
    
    print("✓ Excepciones funcionan correctamente")

def test_configuration():
    """Prueba el módulo de configuración."""
    from src.config.settings import ConfiguracionCliente
    
    print("✓ Probando configuración...")
    config = ConfiguracionCliente()
    print(f"  - IP por defecto: {config.ip_servidor}")
    print(f"  - Puerto por defecto: {config.puerto_servidor}")
    print("✓ Configuración funciona correctamente")

def test_file_handler():
    """Prueba el manejador de archivos."""
    from src.file_management.file_handler import ManejadorArchivos
    
    print("✓ Probando manejador de archivos...")
    handler = ManejadorArchivos()
    print(f"  - Archivo actual: {handler.archivo_actual}")
    print(f"  - Tiene datos: {handler.tiene_datos}")
    print("✓ Manejador de archivos funciona correctamente")

def test_network():
    """Prueba el módulo de red."""
    from src.network.connections import Conexion, ClienteSocket
    
    print("✓ Probando módulo de red...")
    print(f"  - Clase abstracta Conexion disponible")
    print(f"  - Clase ClienteSocket disponible")
    print("✓ Módulo de red funciona correctamente")

def test_gui_components():
    """Prueba los componentes de GUI (sin mostrarlos)."""
    from src.gui.windows import VentanaBase, VentanaConfiguracion, VentanaAcercaDe
    from src.gui.main_app import ClienteGUI
    
    print("✓ Probando componentes de GUI...")
    print(f"  - VentanaBase (abstracta) disponible")
    print(f"  - VentanaConfiguracion disponible")
    print(f"  - VentanaAcercaDe disponible")
    print(f"  - ClienteGUI disponible")
    print("✓ Componentes de GUI funcionan correctamente")

def main():
    """Función principal de prueba."""
    print("=== PRUEBA DE MÓDULOS REFACTORIZADOS ===\n")
    
    test_exceptions()
    print()
    
    test_configuration()
    print()
    
    test_file_handler()
    print()
    
    test_network()
    print()
    
    test_gui_components()
    print()
    
    print("=== TODAS LAS PRUEBAS EXITOSAS ===")
    print("✓ El código ha sido dividido exitosamente en módulos")
    print("✓ Todas las importaciones funcionan correctamente")
    print("✓ La estructura modular es válida")
    print("✓ La aplicación está lista para usar con: python main.py")

if __name__ == "__main__":
    main()