import os
import os; print(os.listdir())
def split_csv(input_file, output_folder, max_size_mb):
    max_size_bytes = max_size_mb * 1024 * 1024

    with open(input_file, 'r') as f:
        header = f.readline()
        part_num = 1
        current_size = 0
        current_part = []
        for line in f:
            current_part.append(line)
            current_size += len(line.encode('utf-8'))

            if current_size >= max_size_bytes:
                output_file = os.path.join(output_folder, f'part_{part_num}.csv')
                with open(output_file, 'w') as out:
                    out.write(header)
                    out.writelines(current_part)

                current_part = []
                current_size = 0
                part_num += 1

        # Write the last part
        if current_part:
            output_file = os.path.join(output_folder, f'part_{part_num}.csv')
            with open(output_file, 'w') as out:
                out.write(header)
                out.writelines(current_part)

# Uso del código
input_file = 'PadronRUC_202504.csv'
output_folder = 'Padron_partes_csv_v'
max_size_mb = 2

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

split_csv(input_file, output_folder, max_size_mb)