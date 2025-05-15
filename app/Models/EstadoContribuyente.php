<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class EstadoContribuyente extends Model
{
    use HasFactory;

    protected $fillable = ['descripcion'];

    public function contribuyentes()
    {
        return $this->hasMany(Contribuyente::class, 'estado_del_contribuyente');
    }
}