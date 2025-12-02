# 📈 European Warrant Calculator v3.0

Calculadora profesional de warrants europeos con implementación completa del modelo **Black-Scholes-Merton**.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/matemadrigal/Calculadora_Warrants)

---

## ✨ Características

### Modelo Matemático
- **Black-Scholes-Merton** completo con dividendos continuos
- **Todas las Greeks**: Delta (Δ), Gamma (Γ), Theta (Θ), Vega (ν), Rho (ρ)
- **Volatilidad implícita** via Newton-Raphson con convergencia garantizada
- **Ratio de conversión** para warrants BNP Paribas y similares

### Activos Soportados
| Región | Índices |
|--------|---------|
| Europa | Euro Stoxx 50, IBEX 35, DAX 40, CAC 40, FTSE 100 |
| EEUU | S&P 500, NASDAQ 100, Dow Jones |
| Asia | Nikkei 225 |

### Interfaz
- Diseño profesional estilo terminal financiero
- Gráficos interactivos de payoff y theta decay
- Responsive (desktop y móvil)
- Auto-fill de parámetros de mercado

---

## 🚀 Despliegue en Vercel

### Opción 1: Un click
Haz click en el botón "Deploy with Vercel" arriba.

### Opción 2: Desde GitHub
1. Fork este repositorio
2. Ve a [vercel.com/new](https://vercel.com/new)
3. Importa tu fork
4. Click "Deploy"

### Opción 3: Vercel CLI
```bash
npm i -g vercel
cd Calculadora_Warrants
vercel --prod
```

---

## 📊 Documentación Matemática

### Black-Scholes-Merton

Para una opción europea:

**Call**: 
$$C = S \cdot e^{-qT} \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)$$

**Put**: 
$$P = K \cdot e^{-rT} \cdot N(-d_2) - S \cdot e^{-qT} \cdot N(-d_1)$$

Donde:
$$d_1 = \frac{\ln(S/K) + (r - q + \sigma^2/2)T}{\sigma\sqrt{T}}$$
$$d_2 = d_1 - \sigma\sqrt{T}$$

### Greeks

| Greek | Fórmula | Interpretación |
|-------|---------|----------------|
| Delta (Δ) | $e^{-qT} \cdot N(d_1)$ | Sensibilidad al spot |
| Gamma (Γ) | $\frac{e^{-qT} \cdot \phi(d_1)}{S \cdot \sigma \cdot \sqrt{T}}$ | Curvatura del delta |
| Theta (Θ) | Ver código | Decay temporal (€/día) |
| Vega (ν) | $S \cdot e^{-qT} \cdot \phi(d_1) \cdot \sqrt{T}$ | Sensibilidad a volatilidad |
| Rho (ρ) | $K \cdot T \cdot e^{-rT} \cdot N(d_2)$ | Sensibilidad a tasa |

### Warrant vs Opción

El precio del warrant incorpora el **ratio de conversión**:

$$\text{Precio Warrant} = \text{Precio BS} \times \text{Ratio}$$

Breakeven para PUT:
$$\text{BE} = K - \frac{\text{Premium}}{\text{Ratio}}$$

---

## 🧪 Tests

Ejecutar suite de validación matemática:

```bash
node tests/math_validation.js
```

Tests incluidos:
- Normal CDF (Abramowitz & Stegun)
- Black-Scholes vs valores Hull (10th ed.)
- Put-Call Parity
- Greeks properties
- Newton-Raphson convergence
- Edge cases

---

## 📁 Estructura del Proyecto

```
Calculadora_Warrants/
├── index.html          # Aplicación completa (single-file)
├── vercel.json         # Configuración de despliegue
├── README.md           # Este archivo
└── tests/
    └── math_validation.js  # Suite de tests
```

---

## 🛠️ Stack Tecnológico

- **React 18** (via CDN, sin build)
- **Tailwind CSS** (via CDN)
- **Recharts** para visualización
- **Babel Standalone** para JSX

---

## ⚠️ Disclaimer

Esta calculadora es **solo para fines educativos**. No constituye asesoramiento financiero. Los datos de mercado son orientativos y deben verificarse antes de operar.

---

## 📄 Licencia

MIT © Mateo Madrigal
