<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Empresa extends Model
{
    use HasFactory;

    protected $primaryKey = 'ruc';
    public $incrementing = false;
    protected $keyType = 'string';

    protected $fillable = [
        'ruc',
        'estado',
        'condicion',
        'tipo',
        'actividad_pri',
        'actividad_sec',
        'actividad_pri_rev',
        'nro_trab',
        'tipo_facturacion',
        'tipo_contabilidad',
        'comercio_exterior',
        'ubigeo',
        'periodo_publicacion'
    ];
}
