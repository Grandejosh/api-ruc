import os
import csv
import mysql.connector
from mysql.connector import Error
import chardet
from tqdm import tqdm

class CSVtoMySQLProcessor:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'api_ruc',
            'user': 'root',
            'password': '12345AracodePeru',
            'autocommit': False
        }
        self.connection = None
        self.cursor = None
        
        # Mapeo de estados a IDs
        self.estados_mapping = {
            'ACTIVO': 1,
            'ANULACION - ERROR SU': 2,
            'BAJA DE OFICIO': 3,
            'BAJA DEFINITIVA': 4,
            'BAJA MULT.INSCR. Y O': 5,
            'BAJA PROV. POR OFICI': 6,
            'SUSPENSION TEMPORAL': 7,
            'NUM. INTERNO IDENTIF': 8,
            'INHABILITADO-VENT.UN': 9,
            'BAJA PROVISIONAL': 10,
            'OTROS OBLIGADOS': 11
        }
        
        # Aumentar el límite de tamaño de campo para CSV
        csv.field_size_limit(1024 * 1024)  # 1MB

    def connect_to_db(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                print("\nConexión exitosa a MySQL")
                self.cursor = self.connection.cursor(dictionary=True)
                return True
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return False

    def detect_encoding(self, file_path):
        """Detecta la codificación del archivo"""
        with open(file_path, 'rb') as f:
            rawdata = f.read(10000)
            result = chardet.detect(rawdata)
        return result['encoding']

    def clean_string(self, value, max_length=None):
        """Limpia y aplica trim a un string, devuelve None si está vacío"""
        if value is None:
            return None
        value = str(value).strip()
        if not value:
            return None
        if max_length and len(value) > max_length:
            value = value[:max_length]
        return value

    def get_estado_id(self, estado_str):
        """Obtiene el ID de un estado solo si está en los estados definidos"""
        if estado_str is None:
            return 12  # Valor por defecto para estados desconocidos
        
        estado_str = estado_str.strip().upper()
        return self.estados_mapping.get(estado_str, 12)

    def process_row(self, row):
        """Procesa una fila del CSV y devuelve los datos estructurados"""
        try:
            ruc = self.clean_string(row[0], 15) if len(row) > 0 else None
            nombre = self.clean_string(row[1], 150) if len(row) > 1 else None
            estado_str = row[2] if len(row) > 2 else None
            
            # Verificar si el estado está en los definidos
            estado_id = self.get_estado_id(estado_str)
            
            # Si el estado no está en los definidos, concatenar nombre y estado
            if estado_id == 12 and estado_str and nombre:
                estado_clean = self.clean_string(estado_str, 150)
                if estado_clean:
                    nombre_completo = f"{nombre}, {estado_clean}"
                    # Asegurarse de que no exceda el límite de 150 caracteres
                    nombre = nombre_completo[:150] if len(nombre_completo) > 150 else nombre_completo
            elif estado_id == 12 and estado_str and not nombre:
                # Si no hay nombre pero sí estado no reconocido, usar solo el estado
                nombre = self.clean_string(estado_str, 150)
            
            return {
                'ruc': ruc,
                'nombre_o_razon_social': nombre,
                'estado_del_contribuyente': estado_id
            }
        except Exception as e:
            print(f"Error procesando fila: {row} - Error: {str(e)}")
            return None

    def process_file(self, file_path):
        """Procesa un archivo CSV completo"""
        try:
            encoding = self.detect_encoding(file_path)
            print(f"\nProcesando: {os.path.basename(file_path)} - Codificación: {encoding}")

            insert_sql = """
            INSERT INTO contribuyentes 
            (ruc, nombre_o_razon_social, estado_del_contribuyente)
            VALUES (%(ruc)s, %(nombre_o_razon_social)s, %(estado_del_contribuyente)s)
            """

            update_sql = """
            UPDATE contribuyentes SET
                nombre_o_razon_social = %(nombre_o_razon_social)s,
                estado_del_contribuyente = %(estado_del_contribuyente)s
            WHERE ruc = %(ruc)s
            """

            total_rows = inserted = updated = errors = 0

            with open(file_path, 'r', encoding=encoding, errors='replace') as csv_file:
                # Primera pasada para contar líneas
                total_lines = sum(1 for _ in csv_file)
                csv_file.seek(0)
                
                # Configurar lector CSV con separador ; y manejo de líneas largas
                csv_reader = csv.reader(csv_file, delimiter=';')
                next(csv_reader)  # Saltar encabezado

                for row in tqdm(csv_reader, total=total_lines-1, desc="Procesando"):
                    total_rows += 1
                    
                    try:
                        if len(row) < 3:
                            errors += 1
                            continue

                        processed = self.process_row(row)
                        if not processed or not processed['ruc']:
                            errors += 1
                            continue

                        self.cursor.execute("SELECT 1 FROM contribuyentes WHERE ruc = %s", (processed['ruc'],))
                        exists = self.cursor.fetchone()

                        if exists:
                            self.cursor.execute(update_sql, processed)
                            updated += 1
                        else:
                            self.cursor.execute(insert_sql, processed)
                            inserted += 1

                        if total_rows % 1000 == 0:
                            self.connection.commit()
                    except csv.Error as e:
                        errors += 1
                        print(f"\nError CSV en fila {total_rows}: {e}")
                        continue
                    except Error as e:
                        errors += 1
                        print(f"\nError en DB para RUC {processed['ruc'] if processed else 'DESCONOCIDO'}: {e}")
                        continue

            self.connection.commit()

            print(f"\nResumen para {os.path.basename(file_path)}:")
            print(f"  - Total filas procesadas: {total_rows}")
            print(f"  - Registros insertados: {inserted}")
            print(f"  - Registros actualizados: {updated}")
            print(f"  - Errores: {errors}")

            return True

        except Exception as e:
            print(f"\nError procesando archivo {file_path}: {str(e)}")
            self.connection.rollback()
            return False

    def process_directory(self, directory='.'):
        """Procesa todos los archivos CSV en un directorio"""
        if not self.connect_to_db():
            return False

        try:
            csv_files = [f for f in os.listdir(directory) if f.lower().endswith('.csv')]
            if not csv_files:
                print("\nNo se encontraron archivos CSV en el directorio")
                return False

            print(f"\nEncontrados {len(csv_files)} archivos CSV para procesar")

            for file in csv_files:
                file_path = os.path.join(directory, file)
                self.process_file(file_path)

            return True

        finally:
            if self.connection and self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
                print("\nConexión a MySQL cerrada")

if __name__ == "__main__":
    try:
        import chardet
        from tqdm import tqdm
    except ImportError:
        print("Instalando dependencias requeridas...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'mysql-connector-python', 'chardet', 'tqdm'])
        import chardet
        from tqdm import tqdm

    processor = CSVtoMySQLProcessor()
    processor.process_directory()