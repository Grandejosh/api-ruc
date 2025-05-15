<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Empresa;
use Illuminate\Support\Facades\Validator;

class ConsultaRucController extends Controller
{
    /**
     * Consulta una empresa por su RUC
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function __construct()
    {
        // Deshabilitar CSRF para el método consulta_ruc
        $this->middleware('web', ['except' => ['consulta_ruc']]);
    }
    public function consulta_ruc(Request $request)
    {
        // Validar el request
        $validator = Validator::make($request->all(), [
            'ruc' => 'required|string|size:11|regex:/^[0-9]+$/'
        ], [
            'ruc.required' => 'El RUC es obligatorio',
            'ruc.size' => 'El RUC debe tener exactamente 11 caracteres',
            'ruc.regex' => 'El RUC solo debe contener números'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Error de validación',
                'errors' => $validator->errors()
            ], 422); // Código 422: Unprocessable Entity
        }

        // Obtener el RUC validado
        $ruc = $request->input('ruc');

        try {
            // Buscar la empresa usando Eloquent
            $empresa = Empresa::where('ruc', $ruc)->first();

            if (!$empresa) {
                return response()->json([
                    'success' => false,
                    'message' => 'RUC no encontrado'
                ], 404); // Código 404: Not Found
            }

            return response()->json([
                'success' => true,
                'data' => $empresa
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error al realizar la consulta',
                'error' => $e->getMessage()
            ], 500); // Código 500: Internal Server Error
        }
    }
}
