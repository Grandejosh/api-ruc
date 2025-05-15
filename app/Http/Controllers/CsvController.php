<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Empresa;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;

class CsvController extends Controller
{
    public function procesar(Request $request)
{
    if (!$request->hasFile('archivos_csv')) {
        return redirect()->back()->with('error', 'No se encontraron archivos para subir.');
    }

    $archivos = $request->file('archivos_csv');
    $registrosProcesados = 0;
    $errores = [];

    DB::beginTransaction();

    try {
        foreach ($archivos as $archivo) {
            if (!$archivo->isValid() || $archivo->getClientOriginalExtension() !== 'csv') {
                $errores[] = "El archivo {$archivo->getClientOriginalName()} no es válido.";
                continue;
            }

            // Guardar el archivo temporalmente
            $path = $archivo->storeAs('archivos', $archivo->getClientOriginalName());

            // Procesar el archivo CSV
            $file = Storage::path($path);
            $handle = fopen($file, 'r');
            
            // Saltar la primera línea (encabezado)
            fgetcsv($handle, 0, ',');
            
            while (($data = fgetcsv($handle, 0, ',')) !== false) {
                // Validar que tenga suficientes columnas
                if (count($data) < 16) {
                    $errores[] = "Fila con formato incorrecto en {$archivo->getClientOriginalName()}";
                    continue;
                }

                try {
                    Empresa::updateOrCreate(
                        ['ruc' => $data[0]], // Buscar por RUC
                        [
                            'estado' => strtoupper($data[1]) === 'ACTIVO',
                            'condicion' => $data[2] ?? null,
                            'tipo' => $data[3] ?? null,
                            'actividad_pri' => $data[4] ?? null,
                            'actividad_sec' => $data[5] ?? null,
                            'actividad_pri_rev' => $data[6] ?? null,
                            'nro_trab' => is_numeric($data[7]) ? (int)$data[7] : null,
                            'tipo_facturacion' => $data[8] ?? null,
                            'tipo_contabilidad' => $data[9] ?? null,
                            'comercio_exterior' => $data[10] ?? null,
                            'ubigeo' => $data[11] ?? null,
                            'periodo_publicacion' => $data[15] ?? null,
                        ]
                    );
                    $registrosProcesados++;
                } catch (\Exception $e) {
                    $errores[] = "Error al procesar RUC {$data[0]}: " . $e->getMessage();
                }
            }
            
            fclose($handle);
            // Opcional: Eliminar el archivo después de procesarlo
            Storage::delete($path);
        }

        DB::commit();

        $mensaje = "Se procesaron {$registrosProcesados} registros exitosamente.";
        if (!empty($errores)) {
            $mensaje .= " Se encontraron " . count($errores) . " errores.";
        }

        return redirect()->back()
            ->with('success', $mensaje)
            ->with('errors', $errores);

    } catch (\Exception $e) {
        DB::rollBack();
        return redirect()->back()
            ->with('error', 'Error general: ' . $e->getMessage());
    }
}
}
