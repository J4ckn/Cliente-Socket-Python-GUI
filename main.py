"""
Punto de entrada principal de la aplicación Cliente de Envío de Datos.

Este módulo contiene la función main() que inicializa y ejecuta
la aplicación de interfaz gráfica del cliente socket.
"""

import tkinter as tk
from tkinter import messagebox

from src.gui.main_app import ClienteGUI


def main():
    """
    Función principal de la aplicación.
    
    Punto de entrada que inicializa la aplicación Tkinter,
    crea la instancia principal de ClienteGUI e inicia el
    bucle de eventos de la interfaz gráfica.
    
    Maneja errores fatales durante la inicialización.
    
    Example:
        python main.py  # Ejecuta esta función
    """
    try:
        root = tk.Tk()
        app = ClienteGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error al inicializar la aplicación: {e}")


if __name__ == "__main__":
    main()