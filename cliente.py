import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import pandas as pd
import json

class ClienteGUI:
   
    def __init__(self, master):
        self.master = master
        master.title("Cliente de Envío de Datos")
        master.geometry("500x300")

        self.filepath = None

        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill="both", expand=True)

        #configuración del servidor
        server_frame = ttk.LabelFrame(main_frame, text="Datos del Servidor")
        server_frame.pack(fill=tk.X, pady=10)

        ttk.Label(server_frame, text="IP del Servidor:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_entry = ttk.Entry(server_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.ip_entry.insert(0, "127.0.0.1") #IP local por defecto

        ttk.Label(server_frame, text="Puerto:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_entry = ttk.Entry(server_frame)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.port_entry.insert(0, "65432") #puerto por defecto

        #seleccion de archivo
        file_frame = ttk.LabelFrame(main_frame, text="Selección de Archivo")
        file_frame.pack(fill=tk.X, pady=10)

        self.select_button = ttk.Button(file_frame, text="Cargar Archivo...", command=self.seleccionar_archivo)
        self.select_button.pack(pady=10)

        self.file_label = ttk.Label(file_frame, text="Ningún archivo seleccionado")
        self.file_label.pack(pady=5)

        #boton de envio
        self.send_button = ttk.Button(main_frame, text="Enviar Datos al Servidor", command=self.enviar_datos)
        # MODIFICACIÓN: Hacemos el botón más grande y visible
        self.send_button.pack(pady=10, fill='x', ipady=30)

    def seleccionar_archivo(self):
      
        #tipos de archivo permitidos
        filetypes = (
            ('Archivos de Excel', '*.xlsx *.xls'),
            ('Archivos de texto plano', '*.csv *.txt'),
            ('Todos los archivos', '*.*')
        )
        filepath = filedialog.askopenfilename(title="Abrir archivo", filetypes=filetypes)
        if filepath:
            self.filepath = filepath
            #mostramos solo el nombre del archivo, no la ruta completa
            filename = filepath.split('/')[-1]
            self.file_label.config(text=filename)

    def enviar_datos(self):
       
        if not self.filepath:
            messagebox.showwarning("Archivo no seleccionado", "Por favor, cargue un archivo antes de enviarlo.")
            return

        try:
            #leer el archivo usando pandas
            if self.filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.filepath)
            elif self.filepath.endswith(('.csv', '.txt')):
                #se asume delimitador por coma, se puede adaptar
                df = pd.read_csv(self.filepath)
            else:
                messagebox.showerror("Formato no soportado", "El formato del archivo no es soportado.")
                return
            
            #convertir el dataFrame a formato JSON
            datos_json = df.to_json(orient='records')

            #conectar y enviar al servidor
            ip_servidor = self.ip_entry.get()
            puerto_servidor = int(self.port_entry.get())

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_servidor, puerto_servidor))
                #codificamos el string JSON a bytes para enviarlo
                s.sendall(datos_json.encode('utf-8'))
            
            messagebox.showinfo("Éxito", "Los datos han sido enviados correctamente al servidor.")

        except FileNotFoundError:
            messagebox.showerror("Error de Archivo", "El archivo seleccionado no se encontró.")
        except ConnectionRefusedError:
            messagebox.showerror("Error de Conexión", "No se pudo conectar al servidor. ¿Está encendido?")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteGUI(root)
    root.mainloop()