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
                # Detectar delimitador automáticamente
                delimitador = self._detectar_delimitador(archivo_path)
                
                # Manejo especial para archivos delimitados por espacios
                if delimitador == ' ':
                    # Para archivos delimitados por espacios, intentar diferentes estrategias
                    datos = self._procesar_archivo_espacios(archivo_path)
                else:
                    # Para otros delimitadores, usar el delimitador detectado
                    datos = pd.read_csv(archivo_path, delimiter=delimitador)
            
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
            print(f"Error al parsear el archivo: {e}")
            raise ArchivoError(f"Error al parsear el archivo: {e}")
        except Exception as e:
            raise ArchivoError(f"Error inesperado al cargar el archivo: {e}")
        
    def _detectar_delimitador(self, archivo_path: Path) -> str:
        """
        Detecta automáticamente el delimitador de un archivo CSV/TXT.

        Lee las primeras líneas del archivo y analiza qué delimitador
        es más probable que esté siendo usado (coma, tabulación, punto y coma, espacios).

        Args:
            archivo_path (Path): Ruta al archivo a analizar

        Returns:
            str: El delimitador detectado (',', '\t', ';', ' ')

        Raises:
            ArchivoError: Si no se puede detectar un delimitador válido

        Note:
            Analiza los delimitadores más comunes en orden de preferencia:
            1. Coma (,) - CSV estándar
            2. Tabulación (\t) - TSV
            3. Punto y coma (;) - CSV europeo
            4. Espacios ( ) - Archivos delimitados por espacios
        """
        import csv
        import re

        try:
            # Leer una muestra del archivo para detectar el delimitador
            with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as archivo:
                muestra = archivo.read(2048)  # Leer más caracteres para mejor detección

            # Usar el Sniffer de CSV para detectar el delimitador (excluyendo espacios)
            sniffer = csv.Sniffer()
            delimitadores_csv = [',', '\t', ';']
            delimitadores_todos = [',', '\t', ';', ' ']

            try:
                # Intentar detectar automáticamente con csv.Sniffer
                dialecto = sniffer.sniff(muestra, delimiters=',\t;')
                return dialecto.delimiter
            except csv.Error:
                # Si falla la detección automática, analizar manualmente
                lineas_muestra = [linea.strip() for linea in muestra.split('\n')[:10] if linea.strip()]
                
                if not lineas_muestra:
                    return ','  # Valor por defecto
                
                mejores_resultados = []
                
                for delimitador in delimitadores_todos:
                    try:
                        # Análisis especial para espacios (múltiples espacios = un delimitador)
                        if delimitador == ' ':
                            columnas_por_linea = []
                            for linea in lineas_muestra:
                                # Reemplazar múltiples espacios por uno solo y luego dividir
                                linea_limpia = re.sub(r'\s+', ' ', linea.strip())
                                if linea_limpia:
                                    columnas = len(linea_limpia.split(' '))
                                    columnas_por_linea.append(columnas)
                        else:
                            # Análisis normal para otros delimitadores
                            columnas_por_linea = []
                            for linea in lineas_muestra:
                                if linea:
                                    columnas = len(linea.split(delimitador))
                                    columnas_por_linea.append(columnas)
                        
                        if columnas_por_linea:
                            # Calcular consistencia: todas las líneas deben tener el mismo número de columnas
                            columnas_unicas = set(columnas_por_linea)
                            consistencia = len(columnas_por_linea) / len(columnas_unicas) if columnas_unicas else 0
                            promedio_columnas = sum(columnas_por_linea) / len(columnas_por_linea)
                            
                            # Filtrar resultados con al menos 2 columnas y buena consistencia
                            if promedio_columnas >= 2:
                                mejores_resultados.append({
                                    'delimitador': delimitador,
                                    'consistencia': consistencia,
                                    'promedio_columnas': promedio_columnas,
                                    'columnas_por_linea': columnas_por_linea
                                })
                    
                    except Exception:
                        continue
                
                # Seleccionar el mejor delimitador basado en consistencia y número de columnas
                if mejores_resultados:
                    # Ordenar por consistencia (descendente) y luego por promedio de columnas (descendente)
                    mejor = max(mejores_resultados, 
                              key=lambda x: (x['consistencia'], x['promedio_columnas']))
                    
                    # Verificar que la consistencia sea razonable (al menos 80% de las líneas iguales)
                    if mejor['consistencia'] >= 0.8:
                        return mejor['delimitador']
                
                # Si no se encontró un delimitador consistente, usar coma por defecto
                return ','

        except Exception as e:
            # Si todo falla, usar coma por defecto
            return ','
    
    def obtener_datos_json(self) -> str:
        """
        Convierte los datos cargados a formato JSON.
        
        Transforma el DataFrame interno a una cadena JSON con formato
        'records' que es ideal para transmisión por red. Mantiene la
        codificación UTF-8 para caracteres especiales.
        
        Returns:
            str: Datos en formato JSON como string
            
        Raises:
            ArchivoError: Si no hay datos cargados o hay error en conversión
            
        Note:
            El formato 'records' genera: [{"col1": val1, "col2": val2}, ...]
            que es ideal para transmisión a través de la red.
        
        Example:
            handler = ManejadorArchivos()
            handler.cargar_archivo("datos.csv")
            json_data = handler.obtener_datos_json()
            # json_data contiene: '[{"pais": "Brasil", "año": 2021}, ...]'
            
        Technical Details:
            Usa 'force_ascii=False' para mantener caracteres Unicode.
            Formato 'records' es más eficiente para arrays de objetos.
        """
        if not self.tiene_datos:
            raise ArchivoError("No hay datos cargados")
        
        try:
            return self._datos.to_json(orient='records', force_ascii=False)
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
    
    def _procesar_archivo_espacios(self, archivo_path: Path):
        """
        Procesa archivos delimitados por espacios con manejo inteligente.
        
        Maneja casos complejos donde los datos pueden contener espacios internos
        pero están separados por múltiples espacios entre columnas.
        
        Args:
            archivo_path (Path): Ruta al archivo a procesar
            
        Returns:
            pd.DataFrame: DataFrame con los datos procesados
            
        Raises:
            ArchivoError: Si no se puede procesar el archivo
        """
        try:
            # Leer el archivo línea por línea para análisis manual
            with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as archivo:
                lineas = archivo.readlines()
            
            if not lineas:
                raise ArchivoError("El archivo está vacío")
            
            # Estrategia principal: Procesamiento manual inteligente
            datos_procesados = []
            encabezados = None
            
            for i, linea in enumerate(lineas):
                linea = linea.strip()
                if not linea:
                    continue
                
                # Dividir por espacios
                partes = linea.split()
                
                if i == 0:  # Línea de encabezado
                    encabezados = partes
                    continue
                
                # Para líneas de datos, esperamos 4 columnas: pais, codigo, año, perdida
                if len(partes) >= 4:
                    if len(partes) == 4:
                        # Caso normal: exactamente 4 campos
                        datos_procesados.append(partes)
                    else:
                        # Caso con espacios en nombre de país: unir primeros campos
                        # Las últimas 3 partes son: codigo, año, perdida
                        pais = ' '.join(partes[:-3])
                        codigo = partes[-3]
                        anio = partes[-2]
                        perdida = partes[-1]
                        datos_procesados.append([pais, codigo, anio, perdida])
                elif len(partes) >= 3:
                    # Caso con menos campos (posible error de formato)
                    # Intentar procesar de cualquier manera
                    while len(partes) < 4:
                        partes.append('')  # Rellenar campos faltantes
                    datos_procesados.append(partes[:4])
            
            if encabezados and datos_procesados:
                df = pd.DataFrame(datos_procesados, columns=encabezados)
                
                # Convertir tipos de datos apropiados
                try:
                    if 'anio' in df.columns:
                        df['anio'] = pd.to_numeric(df['anio'], errors='coerce')
                    if 'perdida_ha' in df.columns:
                        df['perdida_ha'] = pd.to_numeric(df['perdida_ha'], errors='coerce')
                except Exception:
                    pass  # Si falla la conversión, mantener como string
                
                return df
            
            # Si falla el procesamiento manual, intentar estrategia básica
            return pd.read_csv(archivo_path, sep=r'\s+', engine='python')
            
        except Exception as e:
            raise ArchivoError(f"Error al procesar archivo con espacios: {e}")
    
    def _procesar_columnas_fijas(self, archivo_path: Path, lineas: list):
        """
        Procesa archivo usando posiciones fijas de columnas.
        
        Args:
            archivo_path (Path): Ruta al archivo
            lineas (list): Líneas del archivo
            
        Returns:
            pd.DataFrame: DataFrame procesado
        """
        # Analizar la primera línea de datos para determinar posiciones
        if len(lineas) < 2:
            raise ArchivoError("Archivo no tiene suficientes datos")
        
        linea_encabezado = lineas[0].rstrip('\n\r')
        linea_datos = lineas[1].rstrip('\n\r')
        
        # Detectar posiciones de las columnas basándose en espacios múltiples
        import re
        
        # Encontrar grupos de espacios múltiples (2 o más espacios)
        posiciones_separadores = []
        for match in re.finditer(r'  +', linea_datos):
            posiciones_separadores.append((match.start(), match.end()))
        
        if len(posiciones_separadores) >= 2:  # Al menos 3 columnas
            # Definir anchos de columnas basándose en los separadores
            anchos = []
            inicio = 0
            
            for inicio_sep, fin_sep in posiciones_separadores:
                anchos.append(inicio_sep - inicio)
                inicio = fin_sep
            
            # Última columna
            anchos.append(len(linea_datos) - inicio)
            
            # Usar read_fwf (fixed width format)
            return pd.read_fwf(archivo_path, widths=anchos, header=0)
        
        raise ArchivoError("No se pudo determinar estructura de columnas")