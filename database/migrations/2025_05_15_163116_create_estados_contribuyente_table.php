<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('estados_contribuyente', function (Blueprint $table) {
            $table->id();
            $table->string('descripcion', 35);
        });

        // Insertar estados específicos solicitados
        DB::table('estados_contribuyente')->insert([
            ['descripcion' => 'ACTIVO'],
            ['descripcion' => 'ANULACION - ERROR SU'],
            ['descripcion' => 'BAJA DE OFICIO'],
            ['descripcion' => 'BAJA DEFINITIVA'],
            ['descripcion' => 'BAJA MULT.INSCR. Y O'],
            ['descripcion' => 'BAJA PROV. POR OFICI'],
            ['descripcion' => 'SUSPENSION TEMPORAL'],
            ['descripcion' => 'NUM. INTERNO IDENTIF'],
            ['descripcion' => 'INHABILITADO-VENT.UN'],
            ['descripcion' => 'BAJA PROVISIONAL'],
            ['descripcion' => 'OTROS OBLIGADOS'],
            ['descripcion' => 'OTROS o DESCONOCIDO'],
        ]);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('estados_contribuyente');
    }
};