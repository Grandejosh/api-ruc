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
        Schema::create('contribuyentes', function (Blueprint $table) {
            $table->string('ruc', 15)->primary();
            $table->string('nombre_o_razon_social', 100);
            $table->unsignedBigInteger('estado_del_contribuyente');
            
            // Definir la clave foránea
            $table->foreign('estado_del_contribuyente')
                  ->references('id')
                  ->on('estados_contribuyente')
                  ->onDelete('restrict'); // o 'cascade' según necesites
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('contribuyentes', function (Blueprint $table) {
            $table->dropForeign(['estado_del_contribuyente']);
        });
        
        Schema::dropIfExists('contribuyentes');
    }
};