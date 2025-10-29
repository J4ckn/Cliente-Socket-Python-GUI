# Cliente Socket Python GUI

## Descripción del Proyecto

Este es un proyecto universitario que implementa la parte **cliente** de una aplicación cliente-servidor para el envío de datos de deforestación. Está desarrollado en Python con una **arquitectura orientada a objetos** y una interfaz gráfica de usuario (GUI) construida con Tkinter que permite seleccionar y enviar archivos de datos al servidor correspondiente.

### Contexto del Proyecto

Este cliente funciona en conjunto con el [servidor de datos de deforestación](https://github.com/EsotericHog/server_socket_python_gui), formando un sistema completo de comunicación por sockets para el intercambio de datasets sobre deforestación global.

## Características Principales

- **Arquitectura Modular**: Código organizado en módulos separados por responsabilidades
- **Programación Orientada a Objetos**: Implementación usando principios OOP (herencia, composición, abstracción)
- **Interfaz Gráfica Intuitiva**: GUI desarrollada con Tkinter para facilitar la interacción del usuario
- **Soporte Múltiples Formatos**: Compatible con archivos Excel (`.xlsx`, `.xls`) y archivos de texto plano (`.csv`, `.txt`)
- **Comunicación por Sockets**: Utiliza sockets TCP para enviar datos al servidor de forma confiable
- **Configuración Persistente**: Sistema de configuración con archivo config.ini para guardar IP y puerto del servidor
- **Menú de Configuración**: Acceso a configuración del servidor desde la barra de menú
- **Procesamiento de Datos**: Utiliza pandas para leer y procesar los archivos antes del envío
- **Información del Proyecto**: Ventana "Acerca de" con detalles del proyecto y enlaces al servidor
- **Manejo Robusto de Errores**: Jerarquía de excepciones personalizadas y validación completa
- **Documentación Completa**: Todas las clases y métodos están completamente documentados

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

## Estructura del Proyecto

El proyecto ha sido refactorizado siguiendo principios de **arquitectura modular** y **programación orientada a objetos**:

```
Cliente-Socket-Python-GUI/
├── main.py                    # 🚀 Punto de entrada principal
├── cliente.py                 # 📄 Archivo original (conservado para referencia)
├── config.ini                 # ⚙️ Configuración persistente
├── Dataset_Deforestacion.csv  # 📊 Archivo de datos de ejemplo
├── README.md                  # 📖 Documentación del proyecto
├── test_modules.py            # 🧪 Script de prueba de módulos
└── src/                       # 📁 Código fuente
    ├── __init__.py
    ├── core/                  # 🔧 Componentes fundamentales
    │   ├── __init__.py
    │   └── exceptions.py      # ⚠️ Jerarquía de excepciones personalizadas
    ├── config/                # ⚙️ Gestión de configuración
    │   ├── __init__.py
    │   └── settings.py        # 🔧 ConfiguracionCliente
    ├── file_management/       # 📂 Manejo y procesamiento de archivos
    │   ├── __init__.py
    │   └── file_handler.py    # 📊 ManejadorArchivos
    ├── network/               # 🌐 Comunicación de red
    │   ├── __init__.py
    │   └── connections.py     # 🔌 Conexion (ABC), ClienteSocket
    └── gui/                   # 🖥️ Interfaz gráfica de usuario
        ├── __init__.py
        ├── main_app.py        # 🖼️ ClienteGUI (aplicación principal)
        └── windows.py         # 🪟 Ventanas secundarias (configuración, acerca de)
```

### Módulos y Responsabilidades

#### 🔧 **Core Module** (`src/core/`)
- **`exceptions.py`**: Jerarquía de excepciones personalizadas
  - `ClienteError`: Excepción base del sistema
  - `ConexionError`: Errores de conexión de red
  - `ArchivoError`: Errores de procesamiento de archivos
  - `ConfiguracionError`: Errores de configuración

#### ⚙️ **Config Module** (`src/config/`)
- **`settings.py`**: Gestión de configuración persistente
  - `ConfiguracionCliente`: Manejo de IP, puerto y persistencia

#### 📂 **File Management Module** (`src/file_management/`)
- **`file_handler.py`**: Procesamiento de archivos de datos
  - `ManejadorArchivos`: Validación, carga y conversión a JSON

#### 🌐 **Network Module** (`src/network/`)
- **`connections.py`**: Comunicación de red
  - `Conexion`: Clase abstracta base para conexiones
  - `ClienteSocket`: Implementación TCP con context manager

#### 🖥️ **GUI Module** (`src/gui/`)
- **`main_app.py`**: Aplicación principal
  - `ClienteGUI`: Interfaz principal y coordinación de módulos
- **`windows.py`**: Ventanas secundarias
  - `VentanaBase`: Clase abstracta para ventanas modales
  - `VentanaConfiguracion`: Ventana de configuración del servidor
  - `VentanaAcercaDe`: Ventana de información del proyecto

### Principios de Diseño Implementados

- **🏗️ Separación de Responsabilidades**: Cada módulo tiene una responsabilidad específica
- **🔄 Reutilización de Código**: Componentes modulares reutilizables
- **🏛️ Herencia y Abstracción**: Clases abstractas base (ABC) para definir contratos
- **🔧 Composición**: La aplicación principal usa composición para coordinar módulos
- **⚠️ Manejo Robusto de Errores**: Jerarquía de excepciones personalizada
- **📚 Documentación Completa**: Docstrings detallados en todas las clases y métodos

## Instalación y Configuración

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

2. Instala las dependencias:
```bash
pip install pandas
```

3. Ejecuta la aplicación:
```bash
python main.py
```

## Uso del Cliente

1. **Iniciar la Aplicación**: Ejecuta `python main.py` para abrir la interfaz gráfica

2. **Configurar Servidor** (si es necesario): 
   - Ve al menú "Configuración > Servidor..."
   - Ingresa la IP del servidor (por defecto: `127.0.0.1`)
   - Especifica el puerto (por defecto: `65432`)
   - Haz clic en "Guardar" para persistir la configuración

3. **Seleccionar Archivo**:
   - Haz clic en "Seleccionar Archivo..."
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

El cliente incluye un **sistema robusto de manejo de errores** con jerarquía de excepciones personalizadas:

### Jerarquía de Excepciones

- **`ClienteError`**: Excepción base para todos los errores del sistema
  - **`ConexionError`**: Errores específicos de conexión de red
    - Timeouts de conexión
    - Servidor no disponible
    - Errores de resolución DNS
  - **`ArchivoError`**: Errores de procesamiento de archivos
    - Archivo no encontrado
    - Formato no compatible
    - Datos corruptos o inválidos
  - **`ConfiguracionError`**: Errores de configuración
    - Puerto fuera de rango
    - IP inválida
    - Archivo de configuración corrupto

### Validaciones Implementadas

- **Archivo no seleccionado**: Advertencia si se intenta enviar sin seleccionar archivo
- **Formato no soportado**: Error si el archivo no es compatible
- **Archivo no encontrado**: Error si el archivo seleccionado no existe
- **Error de conexión**: Error si no se puede conectar al servidor
- **Validación de datos**: Verificación de estructura y tipos de datos
- **Errores generales**: Manejo de excepciones inesperadas con logging detallado

## Arquitectura Técnica

### Patrones de Diseño Implementados

- **🏛️ Template Method**: `VentanaBase` define estructura común para ventanas modales
- **🔧 Composition Pattern**: `ClienteGUI` compone funcionalidades de otros módulos
- **🔄 Abstract Base Classes (ABC)**: `Conexion` y `VentanaBase` definen contratos
- **🔒 Context Manager**: `ClienteSocket` implementa gestión automática de recursos
- **⚠️ Exception Hierarchy**: Jerarquía personalizada para manejo granular de errores

### Principios SOLID Aplicados

- **🔹 Single Responsibility**: Cada clase tiene una responsabilidad específica
- **🔹 Open/Closed**: Extensible sin modificar código existente
- **🔹 Liskov Substitution**: Las subclases pueden sustituir a sus clases base
- **🔹 Interface Segregation**: Interfaces específicas en lugar de generales
- **🔹 Dependency Inversion**: Dependencias hacia abstracciones, no implementaciones

### Detalles de Implementación

- **🐍 Python 3.x**: Lenguaje principal con tipado opcional (typing)
- **🖼️ Tkinter**: Framework GUI nativo multiplataforma
- **📊 Pandas**: Procesamiento eficiente de datos estructurados
- **🔌 Socket**: Comunicación TCP/IP de bajo nivel
- **⚙️ ConfigParser**: Gestión de configuración persistente
- **📝 JSON**: Formato de intercambio de datos estándar
- **📚 Docstrings**: Documentación completa siguiendo estándares PEP 257

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

### Arquitectura Modular
- **📦 Estructura de Paquetes**: Organización jerárquica con `__init__.py`
- **🔄 Importaciones Relativas**: Sistema de imports optimizado entre módulos
- **🧪 Testing**: Script `test_modules.py` para verificación de funcionalidad
- **📝 Type Hints**: Tipado opcional para mejor documentación y IDE support

### Comunicación de Red
- **🔌 Protocolo**: TCP mediante sockets Python estándar
- **📝 Encoding**: Todos los datos se envían codificados en UTF-8
- **📋 Formato de Intercambio**: JSON para máxima compatibilidad
- **🔒 Context Manager**: Gestión automática de recursos de socket

### Interfaz Gráfica
- **🖼️ GUI Framework**: Tkinter para interfaces nativas multiplataforma
- **🪟 Ventanas Modales**: Sistema de ventanas secundarias con `VentanaBase`
- **⚙️ Configuración Persistente**: Archivo `config.ini` con validación
- **🎨 UX/UI**: Interfaz intuitiva con retroalimentación visual

### Compatibilidad
- **🐍 Python 3.x**: Compatible con versiones modernas de Python
- **🖥️ Multiplataforma**: Windows, Linux, macOS
- **📊 Formatos de Datos**: Excel (.xlsx, .xls), CSV, TXT
- **🌐 Red**: IPv4/IPv6, localhost y conexiones remotas

## Proyecto Universitario

Este es un proyecto académico que demuestra conocimientos avanzados en:

### 🏛️ **Programación Orientada a Objetos**
- Herencia y polimorfismo con clases abstractas
- Composición para coordinar módulos independientes
- Encapsulación y separación de responsabilidades
- Principios SOLID aplicados consistentemente

### 🌐 **Comunicación de Red**
- Programación con sockets TCP/IP en Python
- Arquitectura cliente-servidor distribuida
- Protocolos de comunicación y manejo de errores de red
- Context managers para gestión de recursos

### 🏗️ **Arquitectura de Software**
- Diseño modular con separación clara de responsabilidades
- Patrones de diseño (Template Method, Composition, ABC)
- Estructura de paquetes Python profesional
- Documentación técnica completa

### 📊 **Procesamiento de Datos**
- Manejo de formatos múltiples (Excel, CSV, JSON)
- Validación y transformación de datos con pandas
- Persistencia de configuración
- Manejo robusto de errores de datos

### 🖥️ **Desarrollo de Interfaces**
- Interfaces gráficas nativas con Tkinter
- Diseño UX/UI intuitivo y responsivo
- Ventanas modales y gestión de estado
- Retroalimentación visual al usuario

### 🔧 **Ingeniería de Software**
- Testing y verificación de módulos
- Refactoring de código monolítico a modular
- Gestión de dependencias y entornos virtuales
- Control de versiones y documentación

### Equipo de Desarrollo

- Joaquín Calvillán
- Luciano Flores
- Matías Polanco
- Maximiliano Prieto

---

## 🚀 **Novedades en la Versión Modular**

### ✨ **Mejoras Implementadas**
- 🏗️ **Refactoring Completo**: De código monolítico a arquitectura modular
- 📦 **Estructura de Paquetes**: Organización profesional con `src/` directory
- 🏛️ **Patrones de Diseño**: Implementation de ABC, Template Method y Composition
- ⚠️ **Manejo Robusto de Errores**: Jerarquía personalizada de excepciones
- 📚 **Documentación Completa**: Docstrings detallados en todas las clases y métodos
- 🧪 **Testing Suite**: Script de prueba para verificar todos los módulos
- 🔄 **Compatibilidad**: Mantiene archivo original `cliente.py` para referencia

### 📈 **Beneficios de la Modularización**
- **🔧 Mantenibilidad**: Código más fácil de mantener y extender
- **♻️ Reutilización**: Componentes modulares reutilizables
- **🐛 Debugging**: Errores más fáciles de localizar y corregir
- **👥 Colaboración**: Desarrollo en equipo más efectivo
- **🧪 Testing**: Pruebas unitarias más simples y focalizadas
- **📖 Legibilidad**: Código más claro y autoexplicativo

**Nota**: Para el funcionamiento completo del sistema, asegúrate de tener también el [servidor](https://github.com/EsotericHog/server_socket_python_gui) ejecutándose en el host y puerto especificados.