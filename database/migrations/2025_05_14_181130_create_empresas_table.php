<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('empresas', function (Blueprint $table) {
            $table->string('ruc', 35)->primary();
            $table->boolean('estado');
            $table->string('condicion', 50);
            $table->string('tipo', 60);
            $table->string('actividad_pri', 170);
            $table->string('actividad_sec', 170)->nullable();
            $table->string('actividad_pri_rev', 170)->nullable();
            $table->integer('nro_trab')->unsigned()->nullable();
            $table->string('tipo_facturacion', 30)->nullable();
            $table->string('tipo_contabilidad', 30)->nullable();
            $table->string('comercio_exterior', 26)->nullable();
            $table->string('ubigeo', 12)->nullable();
            $table->string('periodo_publicacion', 6)->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('empresas');
    }
};
