import math
from configuracion import obtener_configuracion

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

def simular_secado(modo, temp_aire, sel_superficie, h_inicial, h_final, peso_quintales, capacidad_max):
    """
    Función principal que simula el proceso de secado.
    Retorna un diccionario con todos los resultados.
    """
    # --- 1. CONFIGURACIÓN DE TEMPERATURA Y ENTORNO ---
    temp_efectiva = 0
    nombre_superficie = "Bandeja Industrial"
    horas_sol_dia = 24  # En industrial se seca 24h continuas
    delta_t = 0

    if modo == "1":
        # MODO INDUSTRIAL
        temp_efectiva = temp_aire
        horas_sol_dia = 24 
    elif modo == "2":
        # MODO SOLAR
        delta_t, nombre_superficie = obtener_ajuste_superficie(sel_superficie)
        temp_efectiva = temp_aire + delta_t
        horas_sol_dia = 8  # En secado solar, asumimos unas 8 horas de secado efectivo al día
    
    # --- 2. CÁLCULOS FÍSICOS ---
    
    # A. Balance de Masa
    peso_kg_inicial = peso_quintales * 45.36
    peso_kg_final = peso_kg_inicial * (100 - h_inicial) / (100 - h_final)
    agua_eliminada = peso_kg_inicial - peso_kg_final
    
    # B. Modelo de Page (Tiempo Base)
    M0 = h_inicial / 100.0
    Mt = h_final / 100.0
    Me = 0.015  # Humedad de equilibrio
    k, n = calcular_constantes_cacao(temp_efectiva)
    
    MR_target = (Mt - Me) / (M0 - Me)
    
    # Evitar error matemático si el objetivo ya se cumplió
    if MR_target <= 0:
        tiempo_base_horas = 0
    else:
        tiempo_base_horas = math.pow((-math.log(MR_target) / k), (1.0 / n))
    
    # C. Factor de Sobrecarga (Espesor de capa)
    factor_penalizacion = 1.0
    if peso_quintales > capacidad_max:
        sobrecarga = peso_quintales / capacidad_max
        factor_penalizacion = sobrecarga ** 1.5
    
    tiempo_total_horas_calor = tiempo_base_horas * factor_penalizacion
    
    # --- 3. PREPARAR RESULTADOS ---
    resultados = {
        'modo': 'INDUSTRIAL' if modo == '1' else 'SOLAR',
        'temp_efectiva': temp_efectiva,
        'nombre_superficie': nombre_superficie,
        'delta_t': delta_t,
        'horas_sol_dia': horas_sol_dia,
        'peso_kg_inicial': peso_kg_inicial,
        'peso_kg_final': peso_kg_final,
        'agua_eliminada': agua_eliminada,
        'factor_penalizacion': factor_penalizacion,
        'tiempo_base_horas': tiempo_base_horas,
        'tiempo_total_horas_calor': tiempo_total_horas_calor,
        'k_calculado': k,
        'n_calculado': n,
        'sobrecarga_detectada': peso_quintales > capacidad_max,
        'porcentaje_capacidad': (peso_quintales / capacidad_max * 100) if capacidad_max > 0 else 0
    }
    
    # Calcular días estimados para modo solar
    if modo == "2":
        dias_estimados = tiempo_total_horas_calor / horas_sol_dia
        resultados['dias_estimados'] = dias_estimados
    
    # Calcular valor estimado de venta
    try:
        # Obtener precio del cacao desde configuración (por defecto 6100 si no está configurado)
        precio_cacao = float(obtener_configuracion('precio_cacao', '6100'))
        
        # Convertir peso final de kg a toneladas métricas
        peso_final_toneladas = peso_kg_final / 1000
        
        # Calcular valor estimado de venta
        valor_estimado_venta = peso_final_toneladas * precio_cacao
        
        resultados['precio_cacao_usd_ton'] = precio_cacao
        resultados['valor_estimado_venta_usd'] = valor_estimado_venta
        resultados['peso_final_toneladas'] = peso_final_toneladas
    except:
        # En caso de error, dejar valores vacíos o cero
        resultados['precio_cacao_usd_ton'] = 0
        resultados['valor_estimado_venta_usd'] = 0
        resultados['peso_final_toneladas'] = 0
    
    return resultados

def validar_entradas(modo, temp_aire, sel_superficie, h_inicial, h_final, peso_quintales, capacidad_max):
    """
    Valida las entradas del usuario y retorna errores si los hay.
    """
    errores = []
    
    # Validar modo
    if modo not in ["1", "2"]:
        errores.append("Debe seleccionar un método de secado válido")
    
    # Validar temperatura según el modo
    try:
        temp_aire = float(temp_aire)
        if modo == "1":  # Industrial
            temp_min = float(obtener_configuracion('temp_min_industrial', '40'))
            temp_max = float(obtener_configuracion('temp_max_industrial', '100'))
        else:  # Solar
            temp_min = float(obtener_configuracion('temp_min_solar', '15'))
            temp_max = float(obtener_configuracion('temp_max_solar', '45'))
        
        if temp_aire < temp_min or temp_aire > temp_max:
            errores.append(f"La temperatura debe estar entre {temp_min}°C y {temp_max}°C")
    except ValueError:
        errores.append("La temperatura debe ser un número válido")
    
    # Validar superficie (solo para modo solar)
    if modo == "2" and sel_superficie not in ["1", "2", "3", "4"]:
        errores.append("Debe seleccionar un tipo de superficie válido")
    
    # Validar humedades
    try:
        h_inicial = float(h_inicial)
        h_final = float(h_final)
        
        # Obtener umbrales desde configuración
        humedad_min = float(obtener_configuracion('humedad_min', '0'))
        humedad_max = float(obtener_configuracion('humedad_max', '100'))
        umbral_advertencia_baja = float(obtener_configuracion('humedad_advertencia_baja', '6'))
        umbral_advertencia_alta = float(obtener_configuracion('humedad_advertencia_alta', '8'))
        
        if h_inicial <= humedad_min or h_inicial > humedad_max:
            errores.append(f"La humedad inicial debe estar entre {humedad_min}% y {humedad_max}%")
        if h_final <= humedad_min or h_final > humedad_max:
            errores.append(f"La humedad final debe estar entre {humedad_min}% y {humedad_max}%")
        if h_inicial <= h_final:
            errores.append("La humedad inicial debe ser mayor que la humedad final")
        # Ya no son errores, solo advertencias que se manejarán en la vista
        if h_final < umbral_advertencia_baja:
            errores.append(f"ADVERTENCIA: Humedad final menor a {umbral_advertencia_baja}% puede quebrar el grano")
        elif h_final > umbral_advertencia_alta:
            errores.append(f"ADVERTENCIA: Humedad final mayor a {umbral_advertencia_alta}% puede generar moho")
    except ValueError:
        errores.append("Los valores de humedad deben ser números válidos")
    
    # Validar pesos
    try:
        peso_quintales = float(peso_quintales)
        capacidad_max = float(capacidad_max)
        
        if peso_quintales <= 0:
            errores.append("El peso debe ser mayor que cero")
        if capacidad_max <= 0:
            errores.append("La capacidad debe ser mayor que cero")
    except ValueError:
        errores.append("Los valores de peso deben ser números válidos")
    
    return errores