import math

def calcular_constantes_cacao(temperatura_c):
    """
    Versión Calibrada V2.
    Calcula k y n basado en la temperatura efectiva del grano.
    """
    # Fórmula empírica para 'k' (Velocidad de secado)
    k = 0.06 * math.exp(0.03 * temperatura_c)
    n = 0.70 
    return k, n

def obtener_ajuste_superficie(opcion):
    """
    Retorna el Delta T (Cambio de temperatura) según el material.
    Basado en la conducción e inercia térmica del material.
    """
    if opcion == "1":   # Cemento
        return 5.0, "Cemento (Retiene calor, acelera el proceso)"
    elif opcion == "2": # Plástico Negro
        return 8.0, "Plástico/Lona (Picos altos de calor, riesgo de condensación)"
    elif opcion == "3": # Caña / Malla
        return 0.0, "Caña/Malla (Ventilación ideal, temperatura ambiente)"
    elif opcion == "4": # Tierra
        return -2.0, "Tierra (Absorbe humedad y enfría, no recomendado)"
    else:
        return 0.0, "Desconocido (Sin ajuste)"

def solicitar_validar_humedad(mensaje, min_val=0, max_val=100, advertencia_baja=None, advertencia_alta=None):
    """Función auxiliar para limpiar el código de validaciones repetitivas"""
    while True:
        try:
            valor = float(input(mensaje))
            if valor > max_val:
                print(f"[ADVERTENCIA] {advertencia_alta}")
                if input("¿Desea corregir? (s/n): ").lower() == 's': continue
            if valor < min_val:
                print(f"[ADVERTENCIA] {advertencia_baja}")
                if input("¿Desea corregir? (s/n): ").lower() == 's': continue
            return valor
        except ValueError:
            print("Por favor, ingrese un número válido.")

def simular_secado():
    print("\n--- SISTEMA HÍBRIDO DE CÁLCULO DE SECADO (v3.0) ---")
    print("1. Secadora Industrial (Gas/Leña)")
    print("2. Secado al Aire Libre (Solar)")
    modo = input("Seleccione el método (1 o 2): ")

    # --- 1. CONFIGURACIÓN DE TEMPERATURA Y ENTORNO ---
    temp_efectiva = 0
    nombre_superficie = "Bandeja Industrial"
    horas_sol_dia = 24 # En industrial se seca 24h continuas

    if modo == "1":
        # MODO INDUSTRIAL
        temp_aire = float(input("\nIngrese Temperatura del Horno (°C): "))
        temp_efectiva = temp_aire
        horas_sol_dia = 24 
    
    elif modo == "2":
        # MODO SOLAR (Tu requerimiento específico)
        print("\n--- CONFIGURACIÓN DE SUPERFICIE ---")
        print("1. Cemento / Hormigón")
        print("2. Plástico Negro / Lona")
        print("3. Tendal de Caña / Malla / Madera")
        print("4. Tierra / Suelo directo")
        sel_superficie = input("¿Sobre qué está el cacao?: ")
        
        delta_t, nombre_superficie = obtener_ajuste_superficie(sel_superficie)
        
        temp_aire = float(input("Ingrese Temperatura Ambiente Promedio (aprox. 10am - 3pm): "))
        
        # La temperatura efectiva es Ambiente + Lo que aporta el suelo
        temp_efectiva = temp_aire + delta_t
        
        print(f"\n[FÍSICA] Superficie: {nombre_superficie}")
        print(f"[FÍSICA] Ajuste de Temperatura: {delta_t:+}°C")
        print(f"[FÍSICA] Temperatura Efectiva en el grano: {temp_efectiva}°C")
        
        # En secado solar, asumimos unas 8 horas de secado efectivo al día
        horas_sol_dia = 8 
    else:
        print("Opción no válida.")
        return

    # --- 2. DATOS DE CARGA (COMÚN PARA AMBOS) ---
    h_inicial = solicitar_validar_humedad(
        "Humedad Inicial (%): ", 
        max_val=70, 
        advertencia_alta="Humedad > 70% es inusual para baba escurrida."
    )
    
    h_final = solicitar_validar_humedad(
        "Humedad Objetivo (%): ", 
        min_val=6, max_val=8,
        advertencia_baja="Menor a 6% el grano se quiebra.",
        advertencia_alta="Mayor a 7-8% genera moho."
    )

    print("\n¿En qué unidad desea ingresar el peso?")
    print("1. Quintales (qq)")
    print("2. Kilos (kg)")
    opcion_peso = input("Seleccione: ")
    
    if opcion_peso == "2":
        peso_kg_inicial = float(input("Kilos a secar: "))
        peso_quintales = peso_kg_inicial / 45.36
    else:
        peso_quintales = float(input("Quintales a secar: "))
        peso_kg_inicial = peso_quintales * 45.36

    # En solar, "Capacidad" se refiere a la capacidad del tendal para esparcir bien el cacao
    label_capacidad = "Capacidad Máxima de la Secadora (qq)" if modo == "1" else "Capacidad Ideal del Tendal/Área (qq)"
    capacidad_max = float(input(f"{label_capacidad}: "))

    # --- 3. CÁLCULOS FÍSICOS ---
    
    # A. Balance de Masa
    peso_kg_final = peso_kg_inicial * (100 - h_inicial) / (100 - h_final)
    agua_eliminada = peso_kg_inicial - peso_kg_final
    
    # B. Modelo de Page (Tiempo Base)
    M0 = h_inicial / 100.0
    Mt = h_final / 100.0
    Me = 0.015 
    k, n = calcular_constantes_cacao(temp_efectiva)
    
    MR_target = (Mt - Me) / (M0 - Me)
    
    # Evitar error matemático si el objetivo ya se cumplió
    if MR_target <= 0:
        tiempo_base_horas = 0
    else:
        tiempo_base_horas = math.pow((-math.log(MR_target) / k), (1.0 / n))
    
    # C. Factor de Sobrecarga (Espesor de capa)
    # Si tienes un tendal para 10qq y pones 20qq, la capa es doble -> Secado lento
    factor_penalizacion = 1.0
    if peso_quintales > capacidad_max:
        sobrecarga = peso_quintales / capacidad_max
        factor_penalizacion = sobrecarga ** 1.5
    
    tiempo_total_horas_calor = tiempo_base_horas * factor_penalizacion

    # --- 4. REPORTE DE RESULTADOS ---
    print(f"\n{'='*40}")
    print(f"       REPORTE DE SECADO ({'INDUSTRIAL' if modo == '1' else 'SOLAR'})")
    print(f"{'='*40}")
    
    print(f"Mermas:")
    print(f" - Entrada: {peso_kg_inicial:.2f} kg | Salida: {peso_kg_final:.2f} kg")
    print(f" - Agua evaporada: {agua_eliminada:.2f} Litros")
    
    if factor_penalizacion > 1.0:
        print(f"\n[ALERTA] ¡SOBRECARGA DETECTADA!")
        print(f" - Estás usando un {(peso_quintales/capacidad_max * 100):.0f}% de la capacidad.")
        print(f" - El aire no circula bien. El proceso será {(factor_penalizacion):.1f}x más lento.")

    print(f"\nEstimación de Tiempo:")
    
    if modo == "1":
        # Reporte Industrial (Horas continuas)
        print(f" > TIEMPO TOTAL: {tiempo_total_horas_calor:.2f} HORAS continuas.")
    else:
        # Reporte Solar (Días)
        dias_estimados = tiempo_total_horas_calor / horas_sol_dia
        print(f" > Horas de Sol Requeridas: {tiempo_total_horas_calor:.1f} horas.")
        print(f" > DÍAS ESTIMADOS (Asumiendo 8h sol/día): {dias_estimados:.1f} DÍAS.")
        if delta_t > 0:
            print(f"   (Más rápido gracias al calor del {nombre_superficie.split()[0]})")
        elif delta_t < 0:
            print(f"   (Más lento debido a la humedad de la {nombre_superficie.split()[0]})")

    print(f"{'='*40}")

if __name__ == "__main__":
    simular_secado()