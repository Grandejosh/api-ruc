<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Contribuyente extends Model
{
    use HasFactory;

    protected $primaryKey = 'ruc';
    public $incrementing = false;
    protected $keyType = 'string';

    protected $fillable = [
        'ruc',
        'nombre_o_razon_social',
        'estado_del_contribuyente',
    ];

    public function estado()
    {
        return $this->belongsTo(EstadoContribuyente::class, 'estado_del_contribuyente');
    }
}