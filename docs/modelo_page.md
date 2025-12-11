# Documentación Técnica: Algoritmo de Secado Industrial de Cacao

## 1\. Introducción

Este documento describe el funcionamiento del algoritmo para la simulación del secado de cacao en hornos industriales. El sistema utiliza el **Modelo Matemático de Page** combinado con una **Regresión Exponencial** para determinar la velocidad de secado en función de la temperatura.

El objetivo es predecir el tiempo necesario ($t$) para reducir la humedad del grano desde un estado inicial (ej. 65%) hasta un estado comercial seguro (7%), considerando variables físicas como peso y capacidad de la máquina.

-----

## 2\. Variables del Sistema

### Entradas (Inputs)

El usuario o los sensores deben proporcionar los siguientes datos:

| Variable | Símbolo | Unidad | Descripción |
| :--- | :---: | :---: | :--- |
| **Temperatura del Aire** | $T$ | °C | Temperatura constante dentro del horno. |
| **Humedad Inicial** | $M_0$ | % | Contenido de agua del grano al inicio (ej. Baba = 60-65%). |
| **Humedad Objetivo** | $M_t$ | % | Meta comercial (Estándar: 7%). |
| **Peso de Carga** | $W$ | Quintales | Cantidad de cacao húmedo ingresado. |
| **Capacidad Máxima** | $C_{max}$ | Quintales | Límite de diseño de la secadora. |

### Constantes del Modelo (Calibración)

Estas constantes definen el comportamiento físico del cacao:

  * **$n$ (Coeficiente de Page):** $0.70$ (Define la forma de la curva de secado).
  * **$M_e$ (Humedad de Equilibrio):** $1.5\%$ (Límite teórico de secado en horno).

-----

## 3\. Lógica Matemática (Paso a Paso)

El algoritmo no utiliza una tabla de búsqueda estática, sino que calcula las variables dinámicamente mediante ecuaciones.

### Paso 1: Cálculo de la Velocidad de Secado ($k$)

La velocidad a la que el agua sale del grano depende del calor. Usamos una **regresión exponencial** (tipo Arrhenius simplificada) para calcular $k$.

$$k = 0.06 \cdot e^{(0.03 \cdot T)}$$

  * *Interpretación:* A mayor temperatura ($T$), el valor de $k$ aumenta exponencialmente, lo que reduce el tiempo de secado.
  * *Nota:* Esta fórmula está calibrada para el rango operativo de 40°C a 75°C.

### Paso 2: Cálculo de la Razón de Humedad ($MR$)

Normalizamos la humedad a una escala de 0 a 1 (donde 1 es mojado y 0 es equilibrio).

$$MR = \frac{M_t - M_e}{M_0 - M_e}$$

Donde los valores de humedad ($M$) se usan en formato decimal (ej. $0.07$ para 7%).

### Paso 3: Resolución de la Ecuación de Page

El modelo de Page establece que $MR = \exp(-k \cdot t^n)$. Despejamos el tiempo ($t$):

$$t = \left( \frac{-\ln(MR)}{k} \right)^{\frac{1}{n}}$$

Esto nos da el **Tiempo Base Teórico** para una capa delgada de cacao.

### Paso 4: Factor de Corrección por Sobrecarga

En ingeniería, si se excede la capacidad de la máquina, la eficiencia cae drásticamente porque el aire no fluye.

Si $W > C_{max}$:

1.  Calculamos la razón de sobrecarga: $R = W / C_{max}$
2.  Aplicamos penalización exponencial: $Factor = R^{1.5}$
3.  $Tiempo_{Real} = Tiempo_{Base} \cdot Factor$

-----

## 4\. Balance de Masa (Ingeniería)

Adicional al tiempo, el algoritmo calcula el cambio físico de masa (agua evaporada).

$$Peso_{Final} = Peso_{Inicial} \cdot \left( \frac{100 - M_0}{100 - M_t} \right)$$

$$Agua_{Evaporada} = Peso_{Inicial} - Peso_{Final}$$

-----

## 5\. Implementación en Código (Python)

A continuación, el script completo utilizando la lógica de regresión calibrada:

```python
import math

class SecadoraIndustrial:
    def __init__(self):
        # Constantes Físicas del Cacao
        self.n = 0.70        # Coeficiente de forma
        self.Me = 0.015      # Humedad de equilibrio (1.5%)

    def calcular_k_regresion(self, temperatura):
        """
        Calcula la constante k usando regresión exponencial.
        Calibrada para que a 60-70°C el proceso dure 10-14 horas.
        """
        # Fórmula: k = A * exp(B * T)
        return 0.06 * math.exp(0.03 * temperatura)

    def simular_proceso(self, temp, h_ini, h_fin, peso_qq, capacidad_qq):
        # 1. Validaciones
        if h_ini <= h_fin: return "Error: H_ini debe ser mayor a H_fin"
        
        # 2. Convertir porcentajes a decimales
        m0 = h_ini / 100.0
        mt = h_fin / 100.0
        me = self.Me

        # 3. Calcular k dinámico
        k = self.calcular_k_regresion(temp)

        # 4. Calcular Moisture Ratio (MR) Objetivo
        mr_target = (mt - me) / (m0 - me)

        # 5. Despejar Tiempo Base (Modelo de Page)
        # t = (-ln(MR) / k) ^ (1/n)
        tiempo_base = math.pow((-math.log(mr_target) / k), (1.0 / self.n))

        # 6. Aplicar Penalización por Sobrecarga
        factor_carga = 1.0
        if peso_qq > capacidad_qq:
            ratio = peso_qq / capacidad_qq
            factor_carga = ratio ** 1.5
        
        tiempo_real = tiempo_base * factor_carga

        # 7. Balance de Masa
        peso_kg_in = peso_qq * 45.36
        peso_kg_out = peso_kg_in * (100 - h_ini) / (100 - h_fin)
        agua_litros = peso_kg_in - peso_kg_out

        return {
            "k_calculado": k,
            "tiempo_estimado_horas": tiempo_real,
            "agua_evaporada_litros": agua_litros,
            "peso_final_kg": peso_kg_out,
            "sobrecarga": factor_carga > 1.0
        }

# --- EJECUCIÓN DE PRUEBA ---
secadora = SecadoraIndustrial()
resultado = secadora.simular_proceso(
    temp=65,           # 65 Grados Celsius
    h_ini=60,          # 60% Humedad inicial
    h_fin=7,           # 7% Humedad final
    peso_qq=10,        # 10 Quintales carga
    capacidad_qq=10    # 10 Quintales capacidad (Carga completa ideal)
)

print(f"Temperatura: 65°C")
print(f"Constante k: {resultado['k_calculado']:.4f}")
print(f"Tiempo Total: {resultado['tiempo_estimado_horas']:.2f} Horas")
print(f"Agua Evaporada: {resultado['agua_evaporada_litros']:.2f} Litros")
```

-----

## 6\. Ejemplo de Trazabilidad

Si ejecutamos el algoritmo con una temperatura de **65°C**:

1.  **Cálculo de k:**
    $$k = 0.06 \cdot e^{(0.03 \cdot 65)} \approx 0.06 \cdot 7.02 \approx \mathbf{0.421}$$
2.  **Cálculo de MR (de 60% a 7%):**
    $$MR = \frac{0.07 - 0.015}{0.60 - 0.015} = \frac{0.055}{0.585} \approx \mathbf{0.094}$$
3.  **Cálculo de Tiempo:**
    $$-\ln(0.094) \approx 2.36$$
    $$\frac{2.36}{0.421} \approx 5.60$$
    $$t = 5.60^{(1/0.7)} \approx 5.60^{1.42} \approx \mathbf{11.6 \text{ horas}}$$

**Conclusión:** El modelo predice correctamente un turno de secado de \~11.5 horas para esa temperatura.