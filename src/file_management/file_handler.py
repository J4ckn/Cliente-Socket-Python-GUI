"""
Módulo de gestión de archivos.

Este módulo maneja la carga, validación y procesamiento de archivos
de datos, incluyendo archivos Excel y CSV/TXT.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.exceptions import ArchivoError


class ManejadorArchivos:
    """
    Clase para encapsular la lógica de lectura y procesamiento de archivos.
    
    Esta clase es responsable de manejar todos los aspectos relacionados
    con la carga, validación y procesamiento de archivos de datos.
    Soporta archivos Excel (.xlsx, .xls) y archivos de texto delimitado
    (.csv, .txt).
    
    Implementa el principio de responsabilidad única al centralizar
    todas las operaciones de archivos en una sola clase, proporcionando
    una interfaz limpia para el resto del sistema.
    
    Class Attributes:
        EXTENSIONES_EXCEL (set): Extensiones de archivos Excel soportadas
        EXTENSIONES_CSV (set): Extensiones de archivos CSV/TXT soportadas
        EXTENSIONES_PERMITIDAS (set): Todas las extensiones permitidas
        
    Attributes:
        _archivo_actual (Path): Ruta del archivo actualmente cargado (privado)
        _datos (DataFrame): Datos del archivo en formato pandas (privado)
        
    Properties:
        archivo_actual: Acceso de solo lectura al archivo actual
        tiene_datos: Indica si hay datos válidos cargados
        
    Example:
        manejador = ManejadorArchivos()
        datos = manejador.cargar_archivo("datos.xlsx")
        if manejador.tiene_datos:
            json_data = manejador.obtener_datos_json()
    """
    
    # Constantes de clase para extensiones soportadas
    EXTENSIONES_EXCEL = {'.xlsx', '.xls'}
    EXTENSIONES_CSV = {'.csv', '.txt'}
    EXTENSIONES_PERMITIDAS = EXTENSIONES_EXCEL | EXTENSIONES_CSV
    
    def __init__(self):
        """
        Inicializa una nueva instancia del manejador de archivos.
        
        Establece el estado inicial sin ningún archivo cargado.
        Todos los atributos se inicializan como None hasta que
        se cargue un archivo válido.
        
        Example:
            manejador = ManejadorArchivos()
            # manejador.tiene_datos será False inicialmente
        """
        self._archivo_actual: Optional[Path] = None
        self._datos: Optional[pd.DataFrame] = None
    
    @property
    def archivo_actual(self) -> Optional[Path]:
        """
        Obtiene la ruta del archivo actualmente cargado.
        
        Property de solo lectura que devuelve el objeto Path
        del archivo que está actualmente cargado en memoria.
        
        Returns:
            Optional[Path]: Ruta del archivo actual o None si no hay archivo
            
        Example:
            if manejador.archivo_actual:
                print(f"Archivo actual: {manejador.archivo_actual.name}")
            else:
                print("No hay archivo cargado")
        """
        return self._archivo_actual
    
    @property
    def tiene_datos(self) -> bool:
        """
        Verifica si hay datos válidos cargados en memoria.
        
        Comprueba que exista un DataFrame válido y que no esté vacío.
        Es útil para validar antes de realizar operaciones que
        requieren datos.
        
        Returns:
            bool: True si hay datos válidos, False en caso contrario
            
        Example:
            if manejador.tiene_datos:
                procesar_datos()
            else:
                print("Cargue un archivo primero")
        """
        return self._datos is not None and not self._datos.empty
    
    def cargar_archivo(self, ruta_archivo: str) -> pd.DataFrame:
        """
        Carga un archivo desde el sistema de archivos y lo procesa.
        
        Lee archivos Excel (.xlsx, .xls) o CSV/TXT (.csv, .txt) y los
        convierte en un DataFrame de pandas para su procesamiento.
        Realiza validaciones completas del archivo y su contenido.
        
        Args:
            ruta_archivo (str): Ruta completa al archivo a cargar
            
        Returns:
            pd.DataFrame: Datos del archivo en formato DataFrame
            
        Raises:
            ArchivoError: Si el archivo no existe, está corrupto, vacío,
                         o tiene un formato no soportado
                         
        Example:
            try:
                datos = manejador.cargar_archivo("/path/to/datos.xlsx")
                print(f"Cargadas {len(datos)} filas de datos")
            except ArchivoError as e:
                print(f"Error al cargar archivo: {e}")
                
        Note:
            Después de una carga exitosa, el archivo queda disponible
            a través de la propiedad 'archivo_actual' y los datos a
            través del método 'obtener_datos_json()'.
        """
        try:
            archivo_path = Path(ruta_archivo)
            
            # Validar existencia del archivo
            if not archivo_path.exists():
                raise ArchivoError(f"El archivo {ruta_archivo} no existe")
            
            # Validar extensión soportada
            if archivo_path.suffix.lower() not in self.EXTENSIONES_PERMITIDAS:
                raise ArchivoError(f"Formato de archivo no soportado: {archivo_path.suffix}")
            
            # Cargar según el tipo de archivo
            if archivo_path.suffix.lower() in self.EXTENSIONES_EXCEL:
                datos = pd.read_excel(archivo_path)
            else:  # CSV o TXT
                datos = pd.read_csv(archivo_path)
            
            # Validar que el archivo no esté vacío
            if datos.empty:
                raise ArchivoError("El archivo está vacío")
            
            # Guardar datos en la instancia
            self._archivo_actual = archivo_path
            self._datos = datos
            
            return datos
            
        except pd.errors.EmptyDataError:
            raise ArchivoError("El archivo está vacío o corrupto")
        except pd.errors.ParserError as e:
            raise ArchivoError(f"Error al parsear el archivo: {e}")
        except Exception as e:
            raise ArchivoError(f"Error inesperado al cargar el archivo: {e}")
    
    def obtener_datos_json(self) -> str:
        """
        Convierte los datos cargados a formato JSON.
        
        Transforma el DataFrame de pandas en una cadena JSON
        con formato de registros (lista de objetos JSON).
        Usa 'ensure_ascii=False' para mantener caracteres Unicode.
        
        Returns:
            str: Datos en formato JSON como cadena de texto
            
        Raises:
            ArchivoError: Si no hay datos cargados o hay error en la conversión
            
        Example:
            if manejador.tiene_datos:
                json_data = manejador.obtener_datos_json()
                print(f"JSON generado: {len(json_data)} caracteres")
                
        Note:
            El formato 'records' genera: [{"col1": val1, "col2": val2}, ...]
            que es ideal para transmisión a través de la red.
        """
        if not self.tiene_datos:
            raise ArchivoError("No hay datos cargados")
        
        try:
            return self._datos.to_json(orient='records', ensure_ascii=False)
        except Exception as e:
            raise ArchivoError(f"Error al convertir datos a JSON: {e}")
    
    def obtener_informacion_archivo(self) -> Dict[str, Any]:
        """
        Obtiene metadatos e información detallada del archivo actual.
        
        Recopila información útil sobre el archivo cargado incluyendo
        datos del sistema de archivos y estadísticas del contenido.
        
        Returns:
            Dict[str, Any]: Diccionario con información del archivo:
                - nombre: Nombre del archivo (sin ruta)
                - ruta: Ruta completa del archivo
                - extension: Extensión del archivo (.xlsx, .csv, etc.)
                - tamaño: Tamaño en bytes del archivo
                - filas: Número de filas de datos
                - columnas: Número de columnas de datos
                Si no hay archivo cargado, retorna diccionario vacío.
                
        Example:
            info = manejador.obtener_informacion_archivo()
            if info:
                print(f"Archivo: {info['nombre']}")
                print(f"Datos: {info['filas']} filas, {info['columnas']} columnas")
                print(f"Tamaño: {info['tamaño']} bytes")
                
        Note:
            El tamaño se obtiene del sistema de archivos, no del DataFrame.
            Las filas y columnas se obtienen del DataFrame cargado.
        """
        if not self._archivo_actual:
            return {}
        
        return {
            'nombre': self._archivo_actual.name,
            'ruta': str(self._archivo_actual),
            'extension': self._archivo_actual.suffix,
            'tamaño': self._archivo_actual.stat().st_size,
            'filas': len(self._datos) if self.tiene_datos else 0,
            'columnas': len(self._datos.columns) if self.tiene_datos else 0
        }