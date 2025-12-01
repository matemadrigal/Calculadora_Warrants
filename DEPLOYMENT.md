# 🚀 Guía de Deployment en Vercel

## European Warrant Calculator - Deployment Instructions

---

## ✅ Archivos de Configuración Creados

Tu proyecto ahora incluye:

- ✅ `vercel.json` - Configuración para servir el HTML como static site
- ✅ `package.json` - Metadata del proyecto (sin dependencias)
- ✅ `index.html` - Tu aplicación React autocontenida

**CONFIRMACIÓN IMPORTANTE:**
- ❌ NO necesitas Node.js/npm instalado
- ❌ NO hay build process
- ❌ NO hay dependencias que instalar
- ✅ Solo HTML estático con CDN links

---

## 📋 OPCIÓN A: Deployment vía Vercel CLI (Terminal)

### Paso 1: Instalar Vercel CLI (una sola vez)

```bash
npm install -g vercel
```

### Paso 2: Login en Vercel

```bash
vercel login
```

Se abrirá tu navegador para autenticarte. Elige tu método preferido (GitHub, GitLab, etc.)

### Paso 3: Deploy desde el directorio del proyecto

```bash
cd /home/user/Calculadora_Warrants
vercel
```

**Durante el primer deployment, Vercel preguntará:**

```
? Set up and deploy "~/Calculadora_Warrants"? [Y/n] → Y
? Which scope do you want to deploy to? → [Tu username]
? Link to existing project? [y/N] → N
? What's your project's name? → warrant-calculator
? In which directory is your code located? → ./
```

**IMPORTANTE - Configuración del proyecto:**

```
? Want to modify these settings? [y/N] → y
```

Luego configura:

- **Build Command:** (dejar vacío o presionar Enter)
- **Output Directory:** `./`
- **Development Command:** (dejar vacío)

### Paso 4: Deploy!

Vercel automáticamente:
1. Subirá tus archivos
2. ❌ NO ejecutará build (porque no hay)
3. Servirá el `index.html` directamente
4. Te dará una URL de producción

**Output esperado:**

```
🔗  Preview: https://warrant-calculator-xxxxx.vercel.app
✅  Production: https://warrant-calculator.vercel.app
```

### Comandos útiles:

```bash
# Deploy a producción directamente
vercel --prod

# Ver deployments
vercel ls

# Ver logs
vercel logs <deployment-url>

# Abrir proyecto en el dashboard
vercel open
```

---

## 📋 OPCIÓN B: Deployment vía Vercel Dashboard (Web + GitHub)

### Paso 1: Preparar el repositorio GitHub

**1.1 Commit los archivos de configuración:**

```bash
cd /home/user/Calculadora_Warrants
git add vercel.json package.json
git commit -m "Add Vercel deployment configuration"
git push origin claude/deploy-warrant-calculator-01QbzQZZnp7LRP1TuHtry6b4
```

**1.2 Hacer merge a main/master** (opcional pero recomendado):

Si quieres deployar desde main:
```bash
# Cambiar a main
git checkout main
git pull origin main

# Merge de tu branch
git merge claude/deploy-warrant-calculator-01QbzQZZnp7LRP1TuHtry6b4

# Push
git push origin main
```

### Paso 2: Conectar con Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Click en **"Add New Project"**
3. Selecciona **"Import Git Repository"**
4. Autoriza Vercel para acceder a tu cuenta de GitHub
5. Busca y selecciona: `matemadrigal/Calculadora_Warrants`

### Paso 3: Configurar el Proyecto

**Framework Preset:**
- Selecciona: **Other** (no React, no Next.js, etc.)

**Root Directory:**
- Dejar: `./` (directorio raíz)

**Build and Output Settings:**

| Setting | Valor | Nota |
|---------|-------|------|
| **Build Command** | (vacío) | Override: dejar en blanco o `echo "No build needed"` |
| **Output Directory** | `./` | Sirve desde raíz |
| **Install Command** | (vacío) | Override: dejar en blanco |

### Paso 4: Environment Variables (OPCIONAL)

Este proyecto NO requiere variables de entorno. Puedes saltar esta sección.

### Paso 5: Deploy!

1. Click en **"Deploy"**
2. Vercel detectará automáticamente el `vercel.json`
3. Servirá el `index.html` como static site
4. **NO ejecutará ningún build process**

⏱️ El deployment toma ~30 segundos

---

## 🔍 Verificación Post-Deployment

### URL del Proyecto

Después del deployment, tendrás:

- **Production URL:** `https://warrant-calculator.vercel.app`
- **Preview URLs:** Una por cada branch/commit (ej: `https://warrant-calculator-git-main-matemadrigal.vercel.app`)

### Checklist de Verificación

1. **Abre la URL en tu navegador**
   - ✅ El título debe ser "European Warrant Calculator"
   - ✅ Los estilos (Tailwind) deben cargar correctamente
   - ✅ El dark theme debe mostrarse

2. **Verifica la consola del navegador (F12)**
   - ❌ NO debe haber errores de carga de CDN
   - ✅ React, Recharts, Babel deben cargar desde unpkg/cdn

3. **Prueba la funcionalidad**
   - ✅ Cambiar entre CALL/PUT funciona
   - ✅ Los inputs aceptan números
   - ✅ Los cálculos se actualizan en tiempo real
   - ✅ Los gráficos se renderizan correctamente

4. **Verifica el responsive design**
   - ✅ Abre en móvil o usa DevTools responsive mode
   - ✅ El layout debe adaptarse correctamente

### En caso de error 404:

Si obtienes 404, verifica en el dashboard de Vercel:
1. Ve a tu proyecto → Settings → General
2. Confirma que el "Root Directory" es `./`
3. Ve a Deployments → Click en el último → Function Logs
4. Busca errores

---

## 🌐 Configurar Dominio Custom (Opcional)

### Si tienes un dominio propio:

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Domains
3. Click en **"Add"**
4. Ingresa tu dominio: `warrants.tudominio.com`

### Configurar DNS:

**Opción A - CNAME (subdominio):**
```
Type: CNAME
Name: warrants
Value: cname.vercel-dns.com
```

**Opción B - A Record (dominio raíz):**
```
Type: A
Name: @
Value: 76.76.21.21
```

⏱️ La propagación DNS toma 5-48 horas

---

## 🔄 Deployments Automáticos

### Si usaste la Opción B (GitHub):

Vercel automáticamente desplegará:

- **Production:** Cada push a `main` → `https://warrant-calculator.vercel.app`
- **Preview:** Cada push a otras branches → URL temporal
- **PR Previews:** Cada Pull Request → URL única

### Desactivar auto-deploy (si lo necesitas):

1. Settings → Git
2. Desactiva "Production Branch" para `main`
3. O desactiva completamente "Git Integration"

---

## 📊 Monitoreo y Analytics

### Vercel Analytics (Gratis para proyectos personales):

1. Ve a tu proyecto → Analytics
2. Click en **"Enable Analytics"**
3. Añade a tu `index.html` (antes del `</head>`):

```html
<script defer src="https://cdn.vercel-analytics.com/v1/script.js"></script>
```

Esto te dará:
- Page views
- Unique visitors
- Top pages
- Devices (mobile/desktop)

---

## 🛠️ Troubleshooting Común

### Error: "No index.html found"

**Solución:** Verifica que `index.html` está en la raíz del proyecto, no en subcarpetas.

```bash
ls -la /home/user/Calculadora_Warrants/
# Debe mostrar: index.html en la raíz
```

### Error: CDN scripts no cargan

**Problema:** CORS o red bloqueando unpkg.com
**Solución:** Verifica en la consola del navegador. Intenta acceder directamente a:
- https://unpkg.com/react@18/umd/react.production.min.js

Si está bloqueado, considera usar otros CDNs:
- jsDelivr: `https://cdn.jsdelivr.net/npm/react@18/...`
- cdnjs: `https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/...`

### Error: "Invalid vercel.json"

**Solución:** Verifica que el JSON es válido:
```bash
cat vercel.json | python3 -m json.tool
```

### Los gráficos no se muestran

**Problema:** Recharts no cargó correctamente
**Solución:** Abre la consola del navegador y verifica:
```javascript
console.log(window.Recharts);
// Debe mostrar un objeto, no undefined
```

---

## 📝 Comandos Rápidos (Resumen)

```bash
# Opción A (CLI) - Deploy en 3 comandos:
npm install -g vercel           # Solo primera vez
vercel login                    # Solo primera vez
vercel --prod                   # Deploy a producción

# Opción B (GitHub) - Setup en 4 pasos:
git add vercel.json package.json
git commit -m "Add Vercel config"
git push origin main
# → Luego importar en vercel.com
```

---

## ✅ Checklist Final

Antes de considerar el deployment completo:

- [ ] Los archivos `vercel.json` y `package.json` están en el repo
- [ ] El deployment completó sin errores
- [ ] La URL de producción carga correctamente
- [ ] Todos los CDN scripts cargan (React, Tailwind, Recharts)
- [ ] La calculadora funciona: inputs, cálculos, gráficos
- [ ] El responsive design funciona en móvil
- [ ] No hay errores en la consola del navegador
- [ ] (Opcional) El dominio custom está configurado
- [ ] (Opcional) Analytics está habilitado

---

## 🎉 ¡Deployment Exitoso!

Tu European Warrant Calculator ahora está online y accesible globalmente.

**Características de Vercel que tienes:**
- ✅ HTTPS automático
- ✅ CDN global (edge caching)
- ✅ Deployment automático desde Git
- ✅ Preview URLs por branch
- ✅ Rollbacks instantáneos
- ✅ 99.99% uptime SLA

**Próximos pasos opcionales:**
1. Configurar un dominio custom
2. Habilitar Vercel Analytics
3. Añadir un favicon personalizado
4. Crear un README.md con el link al demo live
5. Compartir la URL en LinkedIn/GitHub/Portfolio

---

**Documentación oficial:**
- Vercel Docs: https://vercel.com/docs
- Vercel CLI: https://vercel.com/docs/cli
- Troubleshooting: https://vercel.com/support

**¿Necesitas ayuda?**
Revisa el troubleshooting arriba o contacta al soporte de Vercel (responden en ~24h).
