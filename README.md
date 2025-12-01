# European Warrant Calculator

Calculadora profesional de warrants financieros europeos sobre índices (S&P 500, NASDAQ) con implementación completa del modelo Black-Scholes.

## 🎯 Características

- **Warrants Call/Put europeos** sobre índices
- **Modelo Black-Scholes** con dividendos
- **Dos modos de cálculo**:
  - Modo A: Volatilidad → Precio teórico
  - Modo B: Precio mercado → Volatilidad implícita (Newton-Raphson)
- **Métricas clave**: Premium, Delta, P&L, Breakeven, Moneyness
- **Visualizaciones**:
  - Payoff Diagram al vencimiento
  - P&L Evolution (theta decay)
- **Dark theme profesional** inspirado en Bloomberg Terminal

## 🚀 Uso

### Opción 1: Visualización directa
Abre `index.html` en tu navegador.

### Opción 2: Desarrollo React
El código TypeScript está en `warrant-calculator.tsx` para integración en proyectos React.

## 📊 Ejemplo de Validación

**Caso de prueba - PUT ITM:**
```
Tipo: PUT
Spot: 6000
Strike: 6500
Days: 7
Risk-free: 4.5%
Dividend yield: 1.5%
Market price: 0.023 EUR
```

**Resultados esperados:**
- IV: ~15-25%
- Delta: negativo, cercano a -1 (PUT deep ITM)
- Breakeven: ~6477 (Strike - Premium)

## 🔬 Implementación Matemática

### Black-Scholes Europeo
```
Call: S·e^(-q·T)·N(d1) - K·e^(-r·T)·N(d2)
Put:  K·e^(-r·T)·N(-d2) - S·e^(-q·T)·N(-d1)

donde:
d1 = [ln(S/K) + (r - q + σ²/2)·T] / (σ·√T)
d2 = d1 - σ·√T
T = days/365.25
```

### Normal CDF
Aproximación Abramowitz-Stegun con precisión de 7 decimales.

### Volatilidad Implícita
Método Newton-Raphson con:
- Initial guess: 20%
- Max iteraciones: 50
- Tolerancia: 0.0001

### Delta
```
Call: e^(-q·T) · N(d1)
Put:  e^(-q·T) · [N(d1) - 1]
```

## 🛡️ Validaciones

| Campo | Rango | Mensaje de Error |
|-------|-------|------------------|
| Spot, Strike | > 0 | "Debe ser positivo" |
| Days to Expiration | 1-3650 | "Rango 1-3650 días" |
| Risk-Free Rate | 0-50% | "Rango 0-50%" |
| Dividend Yield | 0-20% | "Rango 0-20%" |
| Volatility | 1-200% | "Rango 1-200%" (warning si >100%) |

## 🎨 Stack Tecnológico

- **React 18** + TypeScript (strict mode)
- **TailwindCSS** - Estilos
- **Recharts** - Gráficos interactivos
- **CDN** - Sin build process necesario

## 📱 Responsive Design

- Desktop (>1024px): Layout 40/60 (inputs/resultados)
- Tablet/Mobile: Stack vertical
- Inputs táctiles optimizados (min 16px)

## ⚠️ Limitaciones

- Solo warrants **europeos** (no americanos)
- No incluye Gamma, Vega, Theta (solo Delta)
- No soporta múltiples warrants simultáneos
- Sin exportación a PDF/Excel

## 📖 Uso Educativo

Este proyecto es **solo para fines educativos**. No constituye asesoramiento financiero. Los warrants son productos apalancados de alto riesgo.

## 🔗 Referencias

- Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
- Hull, J. C. (2018). "Options, Futures, and Other Derivatives"
- Abramowitz, M., & Stegun, I. A. (1964). "Handbook of Mathematical Functions"

## 📄 Licencia

MIT License - Uso educativo y personal

---

**Desarrollado con rigor institucional** | Black-Scholes Model Implementation
