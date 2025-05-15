import os

def split_csv(input_file, output_folder, max_size_mb):
    """
    Divide un archivo de texto grande con delimitadores | en múltiples archivos CSV con delimitador ,
    
    Args:
        input_file (str): Ruta del archivo de entrada
        output_folder (str): Carpeta de salida para los archivos divididos
        max_size_mb (int): Tamaño máximo en MB por archivo de salida
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    # Crear carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # Abrir archivo de entrada con codificación UTF-8
        with open(input_file, 'r', encoding='utf-8') as f:
            # Leer encabezado y reemplazar | por ,
            header = f.readline().replace('|', ',')
            
            part_num = 1
            current_size = 0
            current_part = []
            
            for line in f:
                # Procesar línea y agregar al chunk actual
                processed_line = line.replace('|', ',')
                current_part.append(processed_line)
                current_size += len(processed_line.encode('utf-8'))

                # Si se alcanzó el tamaño máximo, escribir archivo
                if current_size >= max_size_bytes:
                    write_part_file(output_folder, part_num, header, current_part)
                    
                    # Reiniciar variables para el siguiente chunk
                    current_part = []
                    current_size = 0
                    part_num += 1

            # Escribir el último chunk si queda contenido
            if current_part:
                write_part_file(output_folder, part_num, header, current_part)

    except UnicodeDecodeError:
        # Si falla con UTF-8, intentar con latin1
        with open(input_file, 'r', encoding='latin1') as f:
            header = f.readline().replace('|', ',')
            
            part_num = 1
            current_size = 0
            current_part = []
            
            for line in f:
                processed_line = line.replace('|', ',')
                current_part.append(processed_line)
                current_size += len(processed_line.encode('utf-8'))

                if current_size >= max_size_bytes:
                    write_part_file(output_folder, part_num, header, current_part)
                    current_part = []
                    current_size = 0
                    part_num += 1

            if current_part:
                write_part_file(output_folder, part_num, header, current_part)

def write_part_file(output_folder, part_num, header, lines):
    """Escribe un archivo parcial con el contenido dado"""
    output_file = os.path.join(output_folder, f'part_{part_num}.csv')
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(header)
        out.writelines(lines)
    print(f'Archivo creado: {output_file}')

if __name__ == '__main__':
    # Configuración
    input_file = 'padron_reducido_ruc.txt'  # Cambiar por tu archivo de entrada
    output_folder = 'partes'                # Carpeta de salida
    max_size_mb = 40                        # Tamaño máximo por archivo (MB)
    
    # Ejecutar división
    split_csv(input_file, output_folder, max_size_mb)
    print("Proceso completado exitosamente!")