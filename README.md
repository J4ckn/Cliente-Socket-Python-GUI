# Cliente Socket Python GUI

## Descripción del Proyecto

Este es un proyecto universitario que implementa la parte **cliente** de una aplicación cliente-servidor para el envío de datos de deforestación. Está desarrollado en Python con una interfaz gráfica de usuario (GUI) construida con Tkinter que permite seleccionar y enviar archivos de datos al servidor correspondiente.

### Contexto del Proyecto

Este cliente funciona en conjunto con el [servidor de datos de deforestación](https://github.com/EsotericHog/server_socket_python_gui), formando un sistema completo de comunicación por sockets para el intercambio de datasets sobre deforestación global.

## Características Principales

- **Interfaz Gráfica Intuitiva**: GUI desarrollada con Tkinter para facilitar la interacción del usuario
- **Soporte Múltiples Formatos**: Compatible con archivos Excel (`.xlsx`, `.xls`) y archivos de texto plano (`.csv`, `.txt`)
- **Comunicación por Sockets**: Utiliza sockets TCP para enviar datos al servidor de forma confiable
- **Configuración Persistente**: Sistema de configuración con archivo config.ini para guardar IP y puerto del servidor
- **Menú de Configuración**: Acceso a configuración del servidor desde la barra de menú
- **Procesamiento de Datos**: Utiliza pandas para leer y procesar los archivos antes del envío
- **Información del Proyecto**: Ventana "Acerca de" con detalles del proyecto y enlaces al servidor
- **Manejo de Errores**: Incluye validación de archivos y manejo de errores de conexión

## Funcionalidad

### Flujo de Trabajo del Cliente

1. **Configuración del Servidor**: El usuario puede configurar la IP y puerto del servidor desde el menú "Configuración > Servidor..." (valores por defecto: `127.0.0.1:65432`)
2. **Selección de Archivo**: Se selecciona un archivo compatible desde el sistema de archivos
3. **Procesamiento**: El archivo se lee y convierte a formato JSON usando pandas
4. **Envío de Datos**: Los datos se envían al servidor mediante una conexión socket TCP usando la configuración guardada
5. **Confirmación**: Se muestra un mensaje de éxito o error según el resultado de la operación

### Formatos de Datos Soportados

- **Excel**: `.xlsx`, `.xls`
- **Texto Plano**: `.csv`, `.txt` (con delimitador por coma)

Los datos deben contener información de deforestación con las siguientes columnas:
- `pais` (string)
- `codigo` (string) 
- `año` (integer)
- `perdida_de_bosques_en_hectareas` (float/integer)

## Instalación y Configuración

### Prerrequisitos

- **Python 3.x** instalado en el sistema
- Las siguientes librerías de Python:
  - `tkinter` (incluida con Python)
  - `pandas`
  - `socket` (incluida con Python)
  - `configparser` (incluida con Python)
  - `webbrowser` (incluida con Python)

### Instalación de Dependencias

```bash
pip install pandas
```

### Ejecución del Cliente

1. Clona este repositorio:
```bash
git clone <URL_DEL_REPOSITORIO>
cd Cliente-Socket-Python-GUI
```

2. Ejecuta el cliente:
```bash
python cliente.py
```

## Uso del Cliente

1. **Iniciar la Aplicación**: Ejecuta `cliente.py` para abrir la interfaz gráfica

2. **Configurar Servidor** (si es necesario): 
   - Ve al menú "Configuración > Servidor..."
   - Ingresa la IP del servidor (por defecto: `127.0.0.1`)
   - Especifica el puerto (por defecto: `65432`)
   - Haz clic en "Guardar" para persistir la configuración

3. **Seleccionar Archivo**:
   - Haz clic en "Cargar Archivo..."
   - Selecciona un archivo compatible (.xlsx, .xls, .csv, .txt)

4. **Enviar Datos**:
   - Haz clic en "Enviar Datos al Servidor"
   - Espera la confirmación de envío exitoso

5. **Información del Proyecto**:
   - Ve al menú "Ayuda > Acerca de..." para ver detalles del proyecto y equipo de desarrollo

## Protocolo de Comunicación

### Formato de Datos

El cliente convierte automáticamente los datos del archivo a formato JSON antes del envío. El formato esperado por el servidor es:

```json
[
  {
    "pais": "Brazil",
    "codigo": "BRA",
    "año": 2021,
    "perdida_de_bosques_en_hectareas": 150000.75
  },
  {
    "pais": "Bolivia", 
    "codigo": "BOL",
    "año": 2021,
    "perdida_de_bosques_en_hectareas": 290000.50
  }
]
```

### Protocolo de Conexión

1. **Establecimiento de Conexión**: Se establece una conexión TCP con el servidor
2. **Envío de Datos**: Los datos JSON se envían codificados en UTF-8 usando `socket.sendall()`
3. **Cierre de Conexión**: La conexión se cierra automáticamente después del envío

## Compatibilidad con el Servidor

Este cliente está diseñado para trabajar específicamente con el [servidor de datos de deforestación](https://github.com/EsotericHog/server_socket_python_gui). Asegúrate de que:

- El servidor esté ejecutándose y escuchando en la IP y puerto configurados
- Los datos del archivo cumplan con el formato esperado por el servidor
- Ambos sistemas estén en la misma red (para entorno local usar `127.0.0.1`)

## Manejo de Errores

El cliente incluye manejo para los siguientes tipos de errores:

- **Archivo no seleccionado**: Advertencia si se intenta enviar sin seleccionar archivo
- **Formato no soportado**: Error si el archivo no es compatible
- **Archivo no encontrado**: Error si el archivo seleccionado no existe
- **Error de conexión**: Error si no se puede conectar al servidor
- **Errores generales**: Manejo de excepciones inesperadas

## Estructura del Código

- `ClienteGUI`: Clase principal que maneja la interfaz gráfica y la lógica del cliente
- `cargar_configuracion()`: Carga la configuración desde config.ini
- `guardar_configuracion()`: Guarda la configuración en config.ini
- `mostrar_configuracion_servidor()`: Ventana modal para configurar servidor
- `mostrar_acerca_de()`: Ventana de información del proyecto
- `seleccionar_archivo()`: Método para seleccionar archivos del sistema
- `enviar_datos()`: Método principal que procesa y envía los datos al servidor

## Configuración Persistente

La aplicación utiliza un archivo `config.ini` para guardar la configuración del servidor:

```ini
[SERVIDOR]
ip = 127.0.0.1
puerto = 65432
```

- **Ubicación**: El archivo se crea automáticamente en el directorio de la aplicación
- **Persistencia**: La configuración se mantiene entre sesiones
- **Validación**: Se valida que el puerto esté en el rango 1-65535
- **Valores por defecto**: IP `127.0.0.1` y Puerto `65432`

## Notas Técnicas

- **Encoding**: Todos los datos se envían codificados en UTF-8
- **Protocolo**: TCP mediante sockets Python estándar
- **Formato de Intercambio**: JSON para máxima compatibilidad
- **GUI Framework**: Tkinter para interfaces nativas multiplataforma

## Proyecto Universitario

Este es un proyecto académico que demuestra:
- Programación con sockets en Python
- Desarrollo de interfaces gráficas con Tkinter
- Procesamiento de datos con pandas
- Arquitectura cliente-servidor
- Manejo de archivos y formatos de datos
- Comunicación en red y protocolos de aplicación
- Persistencia de configuración con archivos INI
- Validación de entrada de datos

### Equipo de Desarrollo

- Joaquín Calvillán
- Luciano Flores
- Matías Polanco
- Maximiliano Prieto

---

**Nota**: Para el funcionamiento completo del sistema, asegúrate de tener también el [servidor](https://github.com/EsotericHog/server_socket_python_gui) ejecutándose en el host y puerto especificados.