# Feedback de socios — correcciones, mejoras y actualizaciones

## ✅ RESUELTO — Stripe activado en modo test (23 Jul 2026)
Se configuraron llaves reales de Stripe (modo test: `pk_test_`/`sk_test_`) y webhook (`whsec_`) apuntando a `https://normaia.ihes.mx/stripe/webhook/` en el `.env` del VPS. Causa del primer intento fallido: `docker compose restart` no relee el `.env`, hay que usar `docker compose up -d web` para que el contenedor se recree con las variables nuevas. Confirmado por Jorge: la compra de prueba con tarjeta `4242 4242 4242 4242` ya funciona end-to-end.

**Siguiente paso confirmado con Jorge: atacar la Fase 1 (correcciones) del plan de abajo antes de seguir con mejoras/rediseños.**

## ✅ RESUELTO — Fase 1 completa (23 Jul 2026), rama `fix/fase1-correcciones-dashboard-planes-correo`
- **#3**: corregido el cálculo de la tarjeta "Dimensiones/Dominios de riesgo" del Dashboard (`surveys/views.py`) — ahora usa los umbrales oficiales de la Guía II por dominio (idénticos a `get_chart_data`) en vez del porcentaje genérico 20/40/60/80%. El % se conserva como dato informativo, pero el nivel/color ya es correcto.
- **#4**: etiqueta corregida "Dimensiones de riesgo" → "Dominios de riesgo" (`surveys/templates/index.html:1169`).
- **#8.1**: insignia "Más popular"/"Mejor valor" corregida en `stripe_planes.html` — ahora compara contra el `key` específico del plan (`nom035_empresarial`, `psico_ilimitado_mensual`, `suite_pro_100`) en vez de una condición que coincidía con los 3 planes del tab a la vez.
- **#1/#2**: reemplazado el correo muerto `n035.ihes@gmail.com` por `normaia.sistemas@gmail.com` en los 7 lugares del código (`views.py`, `middleware.py`, `settings.py`, `default.html` x2, `register-template.html`, `tyc.html` — este último también tenía el `href` desalineado del texto mostrado, corregido también).
- **Correo de bienvenida activado** (decisión de Jorge: ambos): al registrarse, ahora se envía correo de bienvenida al usuario nuevo Y notificación interna a `normaia.sistemas@gmail.com`. Se envuelve en try/except para no romper el registro si el correo falla.
- **Hallazgo adicional en el camino:** los links de verificación de correo/recuperación de contraseña en `register-template.html` apuntaban al dominio viejo `035.ihes.mx` (la instalación obsoleta, no la real `normaia.ihes.mx`) — corregido, de lo contrario el correo de bienvenida y de recuperación hubieran mandado a los usuarios al servidor equivocado.

### Pendiente menor encontrado (no bloqueante, para después): más referencias al dominio viejo `035.ihes.mx`
- `surveys/templates/survey.html:289` — un redirect de JavaScript tras completar una encuesta, usa `https://035.ihes.mx/app/access/...` (formato de deep-link, posiblemente para una app móvil vieja) — revisar si sigue vigente o es código muerto.
- `surveys/templates/tyc.html:172` — mención textual del dominio en los Términos y Condiciones ("...a través del portal ubicado en 035.ihes.mx...") — actualizar cuando se revisen los legales completos.

Documento vivo. Jorge va recopilando observaciones de los socios conforme se las hacen llegar y las pasa a Claude para irlas registrando aquí, verificadas contra el código real. No implica que ya estén implementadas — es el backlog crudo antes de convertir cada punto en una especificación formal (spec → Codex implementa → revisión → staging → merge), como el resto del proyecto.

Fecha de inicio: 22 Jul 2026.

---

## 1. Correo no configurado — bienvenida y recuperación de contraseña

**Observación del socio:** falta configurar el correo para que envíe correo de bienvenida y de recuperación de contraseña.

**Verificado en código (`surveys/views.py`):**
- El SMTP sí está configurado a nivel `settings.py` (Gmail, vía variables de entorno `EMAIL_HOST`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`) — y el VPS ya tiene credenciales reales de Gmail cargadas ahí (confirmado en la sesión de despliegue del VPS).
- **Correo de bienvenida al registrarse:** el código que lo envía está **comentado** (líneas 1966-1968 de `surveys/views.py`, dentro del flujo de `/newuser/`). Es decir, no es un problema de configuración de SMTP — el código simplemente no lo intenta enviar hoy. Hay que descomentarlo/activarlo.
- **Correo de recuperación de contraseña:** el código que lo envía (línea 758, dentro de `PasswordRecover`) **sí está activo**, no comentado. En teoría debería estar enviándose si las credenciales SMTP del VPS son válidas — falta confirmar con una prueba real si efectivamente llega a la bandeja de entrada, antes de asumir que también está roto.

**Siguiente paso:** antes de escribir la especificación de corrección, confirmar con una prueba real en el VPS si el correo de recuperación de verdad no llega (podría ser un problema de configuración real, de spam, o de que el socio no llegó a probarlo). El de bienvenida sí es un gap confirmado en el código.

**ACTUALIZACIÓN — SMTP real del VPS confirmado:** `EMAIL_HOST_USER=normaia.sistemas@gmail.com` (Jorge confirmó acceso a esta cuenta). La cuenta `n035.ihes@gmail.com` que aparece hardcodeada en el código **ya no existe / Jorge no tiene acceso a ella** — hay que reemplazarla en todos lados por `normaia.sistemas@gmail.com`. Se encontraron 7 ocurrencias:

1. **`surveys/views.py:1283` — BUG FUNCIONAL REAL, no solo cosmético.** El endpoint `/contact/` (usado por el formulario de contacto de la landing nueva) envía los mensajes a `n035.ihes@gmail.com`. Como esa cuenta no existe/no es accesible, **todos los mensajes del formulario de contacto se están perdiendo silenciosamente ahora mismo** (el `send_mail()` probablemente falla o rebota, y el usuario ve "enviado" sin que nadie lo reciba). Cambiar a `normaia.sistemas@gmail.com`.
2. `nom035/settings.py:186` — default de respaldo de `EMAIL_HOST_USER` si algún entorno no define la variable por `.env` (VPS ya la tiene bien vía `.env`, pero el default en código debería actualizarse para consistencia en otros entornos).
3. `nom035/middleware.py:4` — `from_email` hardcodeado en un helper de correo casi sin uso (solo lo llama `ExceptionLoggingMiddleware` para avisos de error de sistema, que van a `erick.fcm.0@gmail.com`, correo de un desarrollador anterior — revisar aparte si ese destino también debe actualizarse).
4. `surveys/templates/default.html` (2 menciones) y `surveys/templates/tyc.html` — texto visible al usuario ("contáctanos en...") en páginas que sí se renderizan en producción.
5. `surveys/templates/register-template.html` — texto dentro del correo de confirmación de compra, mencionando ese correo para solicitar factura.

**Pendiente de decidir con Jorge:** ¿corrijo ya estos 7 puntos (cambio de texto/config, bajo riesgo) o se agrupan en una especificación futura junto con el resto de los pendientes de correo (bienvenida comentada, verificar recuperación en vivo)?

---

## 2. Sin carga masiva de empleados por centro de trabajo

**Observación del socio:** cuando son muchos empleados, el usuario tiene que cargarlos uno por uno en el centro de trabajo. Si son 50 o más, debería existir una opción de carga masiva, con una plantilla en Excel o CSV (con uno o dos datos de ejemplo) que el usuario pueda descargar, llenar y volver a subir.

**Estado:** no existe hoy. Es una funcionalidad nueva, no una corrección de bug.

**Consideraciones para la especificación futura (a definir cuando se ataque):**
- Plantilla descargable (XLSX o CSV) con las columnas que ya usa el alta individual de empleado (nombre, género, edad, estado civil, escolaridad, ocupación, departamento, tipo de puesto, tipo de contrato, tipo de empleado, turno, rotación de turno, tiempo en el puesto, experiencia — mismos campos que `Employee`/`EMPLEADOS_DEMO` en `cargar_datos_demo.py`), con 1-2 filas de ejemplo ya llenas.
- Validación de la plantilla al subir (columnas correctas, filas vacías, límites de plan vigentes, etc.)
- Definir qué pasa con filas inválidas: ¿se rechaza todo el archivo o se cargan las válidas y se reportan las que fallaron?

---

## 3. Porcentaje de riesgo incorrecto en la tarjeta "Dimensiones de riesgo" del Dashboard

**Observación del socio:** captura mostrando "Condiciones en el ambiente de trabajo — 71% — ALTO" en el Dashboard, con duda sobre de dónde sale ese porcentaje y si el cálculo real de NOM-035 está bien hecho.

**Verificado contra el texto oficial de la norma (DOF 23/oct/2018, Guías de Referencia II y III, Tabla 3 y Tabla 6):**

Existen DOS calculadoras distintas de nivel de riesgo por dominio en el sistema:

1. **Vista "Resultados completos" (`get_chart_data`, `surveys/views.py` ~línea 1450) — CORRECTA.** Suma los puntos crudos de cada dominio (Cdom) y los compara contra los rangos oficiales específicos de la norma para cada dominio (verificado línea por línea contra la Tabla 6: ej. "Condiciones en el ambiente de trabajo" Nulo&lt;5/Bajo 5-9/Medio 9-11/Alto 11-14/Muy alto≥14 — idéntico al DOF). Esta vista es confiable, es la que genera el reporte oficial descargable.

2. **Tarjeta "Dimensiones de riesgo" del Dashboard principal (`index.html`, calculada en `surveys/views.py` líneas 164-180) — INCORRECTA.** En vez de usar las tablas oficiales, calcula un porcentaje simple (suma de respuestas ÷ máximo posible × 100) y lo clasifica con **cortes genéricos idénticos para los 8 dominios**: &lt;20% Nulo, 20-40% Bajo, 40-60% Medio, 60-80% Alto, 80%+ Muy alto.

**El bug real:** la norma NO usa cortes parejos por dominio — cada dominio tiene su propio rango según su cantidad de reactivos. Ejemplo verificado: para "Carga de trabajo" la norma marca "Muy alto" desde el 46% del máximo, pero el dashboard (con su regla genérica de 80%) no lo marcaría "Muy alto" hasta el 80%. **Esto significa que el dashboard puede estar sub-clasificando el riesgo real de varios dominios** (mostrándolos como "Medio" o "Bajo" cuando la norma ya los consideraría "Alto" o "Muy alto"). En el caso puntual del 71% que vio el socio, coincide por casualidad con "Alto" en ambos métodos (es un dominio pequeño con rango parecido a la regla genérica) — pero no es así para los demás dominios.

**Bug adicional:** la leyenda de interpretación mostrada junto a la tarjeta ("Crítico 1.0-2.49", "Alto 2.5-3.99", etc., en `index.html` líneas 1190-1233) **no corresponde a ninguno de los dos cálculos** — es texto genérico copiado que no coincide ni con el porcentaje ni con el sistema de suma cruda real.

**Alcance de la corrección (pendiente de definir con Jorge):**
- Reemplazar el cálculo de `dimensions_preview` (líneas 164-180) para que reutilice la misma lógica ya correcta de `get_chart_data`, en vez de la fórmula de porcentaje genérico.
- Corregir o quitar la leyenda de interpretación hardcodeada de `index.html` para que corresponda al cálculo real que se termine usando.
- El reporte oficial descargable (PDF) NO necesita cambios — ya está bien.

## 4. Etiqueta incorrecta "Dimensiones de riesgo" en el Dashboard — debería decir "Dominios"

**Observación del socio (Miguel Angel Juárez):** el título dice "Dimensiones de riesgo" pero no son dimensiones, son dominios. Los dominios son 8, las dimensiones son 20.

**Verificado contra el texto oficial de la norma (Tabla 3 de la Guía de Referencia II, DOF 23/oct/2018):** correcto al 100%. La jerarquía real de la norma es Categoría → Dominio → Dimensión → ítem:
- 8 **dominios**: Condiciones en el ambiente de trabajo, Carga de trabajo, Falta de control sobre el trabajo, Jornada de trabajo, Interferencia en la relación trabajo-familia, Liderazgo, Relaciones en el trabajo, Violencia.
- 20 **dimensiones** en total (subdivisiones dentro de los dominios, ej. dentro de "Carga de trabajo": cargas cuantitativas, ritmos de trabajo acelerado, carga mental, cargas psicológicas emocionales, cargas de alta responsabilidad, cargas contradictorias o inconsistentes — 6 dimensiones solo en ese dominio).

**En el código:** `surveys/templates/index.html:1169` tiene el texto `<p class="nom-wp-center-label">Dimensiones de riesgo</p>`, pero lo que se muestra debajo son los 8 dominios (confirmado: `domainsA_dash` en `surveys/views.py` línea 168 tiene exactamente 8 claves, coincide con los 8 dominios oficiales).

**Nota de consistencia:** la vista "Resultados completos" (`workplace_results.html`) ya usa la terminología correcta — tiene pestañas separadas "Categoría / Dominio / Dimensión", los 3 niveles reales de la norma. El error de etiqueta es exclusivo de esta tarjeta del Dashboard.

**Corrección:** cambio de texto de una sola línea, bajo riesgo — "Dimensiones de riesgo" → "Dominios de riesgo" en `index.html:1169`. Se puede aplicar junto con el hallazgo #3 (mismo bloque de la UI).

## 5. PROPUESTA (no es corrección): enriquecer la ficha de detalle del centro de trabajo

**Propuesta del socio:** en la ficha de detalle de un centro de trabajo, mostrar una evaluación/recomendación sugerida por IA — para que si tienes varios centros, puedas ver de un vistazo cuál necesita atención. Además, hoy "Ver detalle" solo lleva a una parte del centro, como si eso fuera todo a lo que tienes acceso, cuando en realidad hay más secciones relacionadas (evidencias, clima laboral).

**Verificado en el código:** confirma el problema. `WorkplaceDetailView`/`workplace_detail.html` hoy solo muestra datos NOM-035 (nombre, dirección, empleados, evaluación) y enlaces a: agregar empleado, resultados de esa evaluación, compartir por WhatsApp, ver planes. **No hay ningún acceso directo desde ahí a Portafolio de Evidencias ni a Clima Laboral de ese mismo centro**, aunque ambos ya existen y están ligados al `Workplace`.

**Limitación estructural encontrada:** el modelo `Candidate` (psicometría) **no está ligado a un centro de trabajo** — pertenece a la cuenta completa (`user`), no a un `Workplace` específico. Esto significa que "tener los accesos de psicometría ahí" no es un simple enlace filtrado; los candidatos no tienen esa relación en la base de datos hoy. Habría que decidir si vale la pena agregarla (cambio de esquema) o dejar psicometría fuera de esta ficha por ahora.

**Mi valoración, dividida en 2 partes de esfuerzo/riesgo muy distinto:**

1. **Enlaces directos a Evidencias y Clima Laboral del centro** — bajo riesgo, esfuerzo bajo-medio. Ambas vistas ya existen y ya reciben `workplace_id`; solo falta agregar los enlaces en `workplace_detail.html`. Recomiendo hacerlo, es una mejora de navegación clara y de bajo riesgo.

2. **Evaluación/recomendación sugerida por IA, indicando qué centro necesita atención** — valiosa para cuentas con varios centros, pero es un alcance mayor:
   - Requiere definir qué significa "necesita atención" (¿nivel de riesgo alto en algún dominio? ¿baja participación? ¿evidencias pendientes? ¿mucho tiempo sin actividad?)
   - Puede resolverse con una regla simple (sin IA, solo lógica condicional barata) o con una llamada real a IA tipo el perfil narrativo ya existente (más costoso, requeriría cachear el resultado para no recalcularlo en cada carga del dashboard)
   - Recomiendo empezar con la versión simple basada en reglas (ej. semáforo de atención por centro) antes de invertir en IA generativa para esto — es más barato, más rápido de implementar, y probablemente resuelve el 80% del valor que busca el socio (identificar de un vistazo qué centro revisar primero).

**Pendiente de decidir con Jorge:** si se prioriza, y si se empieza solo con la parte 1 (enlaces) o también la 2 (indicador de atención).

### 5.1 Mockup concreto recibido — rediseño de la LISTA de Centros de Trabajo (no solo la ficha de detalle)
Jorge compartió un mockup del diseño propuesto para la página "Centros de Trabajo" (la lista, antes de entrar al detalle): tarjetas KPI arriba (Centros de trabajo, Empleados totales, Evaluaciones aplicadas, Cumplimiento NOM-035 %, Riesgo predominante), buscador + filtros por estado/riesgo, y cada centro en una tarjeta con: empleados, % de cumplimiento, nivel de riesgo (badge de color), evaluaciones aplicadas, botones "Ver detalle" y "Dashboard".

Esto **sí resuelve el objetivo original de la propuesta #5** (ver de un vistazo qué centro necesita atención) sin necesitar una llamada a IA generativa — con datos + un badge de nivel de riesgo + filtro por riesgo ya se logra. Confirma mi recomendación de empezar por la versión simple antes de invertir en IA.

**Dos puntos a verificar antes de construirlo:**

1. **El indicador "Nivel de riesgo" por centro debe reutilizar el cálculo correcto** (el de `get_chart_data`, ya verificado contra la norma en el hallazgo #3) — **no** la fórmula de porcentaje genérico que sí está rota en la tarjeta actual del Dashboard. Si se construye este rediseño reutilizando el método incorrecto, se replicaría el mismo bug en una pantalla nueva.

2. **La etiqueta "Cumplimiento NOM-035: 85%"** — hay que definir con precisión qué mide. Si es el % de cuestionarios aplicados/completados (dato que ya existe como `survey_completion` en el sistema), llamarlo "Cumplimiento NOM-035" puede ser engañoso: aplicar el cuestionario es solo una parte de lo que pide la norma (también exige política de prevención, difusión, programas de intervención cuando el riesgo lo amerita, etc. — numerales 5.1 a 5.8). Es el mismo tipo de cuidado que ya aplicamos en el rediseño de la landing (evitar "cumplimiento garantizado/automático"). Sugerencia: renombrar a algo como "Participación" o "Cuestionarios aplicados" si eso es lo que realmente mide, y reservar "Cumplimiento NOM-035" para cuando de verdad se evalúen los requisitos completos de la norma.

## 5.2 PROPUESTA IMPORTANTE — falta un indicador general y recomendaciones automáticas (gap real, no solo cosmético)

**Planteamiento del socio:** la NOM-035 no busca solo clasificar resultados por dominio/categoría — busca que la empresa pueda responder: ¿cuál es el nivel general del centro?, ¿qué porcentaje de dominios está en riesgo?, ¿qué debe hacer la empresa? Propone:
1. Un indicador ejecutivo único ("RIESGO GENERAL — 🟡 EN RIESGO — 3.43/5") con explicación en lenguaje simple.
2. Conteo de cuántos dominios caen en cada nivel (ej. "8 dominios: 4 Favorables, 2 Adecuados, 2 En riesgo, 0 Críticos").
3. Panel de "Acciones prioritarias" — recomendaciones automáticas según los resultados.

**Verificado en el código: este es un vacío real, confirmado.** Grep en `surveys/views.py` no encuentra ningún cálculo de puntaje general ni ningún texto de recomendaciones — el sistema solo calcula y muestra resultados por dominio (`Cdom`) y por categoría (`Ccat`), nunca un total agregado del cuestionario completo, y nunca genera ninguna sugerencia de acción.

**Lo que la norma sí exige y hoy no se cumple:**
- El numeral 7.7 (datos obligatorios del informe) exige explícitamente **"Conclusiones"** e **"Recomendaciones y acciones de intervención"** — hoy el informe no incluye ninguna de las dos.
- La norma SÍ define un puntaje general por cuestionario (llamado `Cfinal` en las Guías II y III), con sus propios rangos oficiales de interpretación (Guía II: Nulo&lt;20, Bajo 20-45, Medio 45-70, Alto 70-90, Muy alto&gt;90; Guía III: Nulo&lt;50, Bajo 50-75, Medio 75-99, Alto 99-140, Muy alto&gt;140) — **esto es exactamente el "RIESGO GENERAL" que propone el socio, y ya está definido oficialmente, solo falta implementarlo.**
- El numeral 8.2 de la norma da un catálogo detallado de acciones recomendadas por tipo de dominio (liderazgo y relaciones, cargas de trabajo, control de trabajo, apoyo social, equilibrio trabajo-familia, reconocimiento, violencia laboral, información y comunicación, capacitación) — es decir, **la norma ya trae su propio catálogo de recomendaciones**, no hay que inventarlas.

**Mi recomendación:**
1. **Indicador general (Cfinal):** implementar directo, es solo sumar todos los ítems del cuestionario y compararlos contra los rangos oficiales ya citados arriba — bajo riesgo, cálculo ya definido por la norma, no requiere criterio nuevo.
2. **Conteo de dominios por nivel:** trivial una vez que se tienen los niveles de cada dominio (ya calculados correctamente en `get_chart_data`, ver hallazgo #3) — solo hay que contarlos y agruparlos.
3. **Recomendaciones automáticas:** recomiendo generarlas basadas en **reglas, tomando el texto directo del numeral 8.2 de la norma** según qué dominios salieron en Medio/Alto/Muy alto — no usar IA generativa libre para esto. Razón: son recomendaciones con implicación legal/normativa, y el numeral 8.2 ya da el catálogo oficial de acciones por dominio — usar ese texto directamente es más seguro, defendible y barato que generar texto nuevo con IA (que podría inventar recomendaciones no alineadas con la norma).

**Nota de consistencia con el hallazgo #4:** el ejemplo del socio dice "8 dimensiones" — igual que en ese hallazgo, técnicamente son **8 dominios** (las dimensiones son 20, subdivisiones dentro de los dominios). Aplicar la misma corrección de término aquí.

**Nota sobre la escala de 4 niveles usada en el ejemplo** (Favorable/Adecuada/En riesgo/Crítica): la norma oficial usa 5 niveles (Nulo/Bajo/Medio/Alto/Muy alto). Hay que decidir si el indicador ejecutivo usa la escala oficial completa de 5 niveles (más alineado con la norma) o una simplificación a 4 (más fácil de comunicar, pero hay que ver cómo se mapea Nulo/Bajo → esos 4).

## 5.3 Mockup completo "Tablero Ejecutivo" — junta 5.1, 5.2 y #6 en una sola pantalla

**Contexto:** mockup integral que combina Riesgo General, Participación, conteos de Dominios/Categorías/Dimensiones, navegación en cascada Dominio → Categoría → Dimensión (así se ve claramente que las dimensiones pertenecen a su dominio, resolviendo el punto de contexto que señala el socio), Hallazgos prioritarios, distribución de niveles (dona), Plan de acción recomendado con prioridad y estado, y comparativo histórico.

**Punto filosófico del socio (correcto):** las decisiones organizacionales se toman sobre dominios y categorías, no sobre dimensiones aisladas — mostrar la jerarquía completa (Dominio > Categoría > Dimensión) en vez de una lista plana de 20 dimensiones sueltas es fiel a cómo la norma realmente estructura el análisis. Buen diseño en ese sentido.

**Dos cosas nuevas a verificar antes de construir:**

1. **"NIVEL DE CUMPLIMIENTO — 85% — Conforme a la NOM-035-STPS-2018"** — esta etiqueta es más fuerte que la de 5.1 ("Cumplimiento NOM-035: 85%"), ahora afirma explícitamente "Conforme a la NOM-035-STPS-2018". Esto es conceptualmente delicado: **el cumplimiento de la norma no se mide por el nivel de riesgo psicosocial resultante** — se mide por si la empresa cumplió las obligaciones documentales/procedimentales del Capítulo 5 (política de prevención, difusión, exámenes cuando corresponda, registros, programa de intervención cuando el riesgo lo amerite, etc.). Una empresa puede tener riesgo bajo y aun así no ser conforme (si nunca hizo la política de prevención), o tener riesgo alto y sí ser conforme (si aplicó todo lo que la norma pide, incluido el programa de intervención correspondiente). Recomiendo **no usar la palabra "Cumplimiento" ni "Conforme a la NOM-035"** para ningún porcentaje derivado de las respuestas de riesgo — usar en su lugar algo como "Participación" (ya está bien separado como su propia tarjeta) o, si se quiere medir cumplimiento real, sería un indicador aparte basado en qué obligaciones documentales de la norma ya se cumplieron (política de prevención cargada, programa de intervención generado, etc.), no en el resultado psicosocial.

2. **"Plan de Acción Recomendado" con columna "Estado" (Pendiente)** — esto es una funcionalidad nueva más grande de lo que se había valorado en el hallazgo #5.2: no es solo mostrar texto de recomendaciones, es **dar seguimiento con estado** a cada acción (marcar como pendiente/en proceso/completada). Verificado: no existe hoy ningún modelo en el código para esto. Buena noticia: esto **sí es exactamente lo que pide el numeral 8.4 de la norma** ("El control de los avances de la implementación del programa" es un requisito explícito del Programa de intervención) — no es sobre-alcance, es implementar un requisito real que hoy falta. Pero sí implica más trabajo: nuevo modelo de datos, CRUD para cambiar el estado, y UI de seguimiento — no es un simple cambio de presentación como el resto.

## PROPUESTA DE PLAN POR FASES (para no atrasar el arranque, según pidió Jorge)

Dado que los hallazgos #3, #4, #5, #5.1, #5.2, #5.3 y #6 en el fondo son partes de una misma iniciativa (mejorar cómo se presentan y se actúa sobre los resultados de NOM-035), propongo agruparlos así:

**Fase 1 — correcciones puntuales, bajo riesgo, listas para atacar ya (son bugs, no funcionalidad nueva):**
- #3: corregir el cálculo de la tarjeta "Dimensiones de riesgo" del Dashboard para que reutilice la lógica correcta ya existente en `get_chart_data`
- #4: corregir la etiqueta "Dimensiones de riesgo" → "Dominios de riesgo"
- #8.1: corregir la insignia "Más popular"/"Mejor valor" que aparece en los 3 planes a la vez
- #1/#2: reemplazar el correo muerto, activar correo de bienvenida (según se decida)

**Fase 2 — indicador general y recomendaciones de solo lectura (dato nuevo, pero cálculo ya definido por la norma, sin necesidad de nuevo modelo de datos):**
- #5.2 parte 1: calcular e implementar el "Riesgo General" (Cfinal) con los rangos oficiales
- #5.2 parte 2: conteo/distribución de dominios por nivel
- #5.2 parte 3: recomendaciones de solo lectura basadas en el catálogo del numeral 8.2 (sin seguimiento de estado todavía)
- #5 parte 1: enlaces directos a Evidencias y Clima Laboral desde la ficha del centro

**Fase 3 — rediseño visual completo + funcionalidad con estado (mayor esfuerzo, requiere nuevo modelo de datos):**
- #6 + #5.3: el "Tablero Ejecutivo" completo con navegación Dominio → Categoría → Dimensión, comparativo histórico
- Plan de acción con seguimiento de estado (nuevo modelo de datos, numeral 8.4)
- #5.1: rediseño de la lista de Centros de Trabajo con KPIs

**Pendiente de decidir con Jorge:** confirmar este orden de fases, o ajustarlo según lo que los socios consideren más urgente.

**DECISIÓN DE JORGE (confirmada):** sí actualizar la vista actual de Resultados hacia algo similar a la propuesta del Tablero Ejecutivo, pero con estas condiciones:
- Basarse en lo que la norma realmente pide (no inflar indicadores, ver notas de 5.2/5.3 sobre "cumplimiento" vs "riesgo")
- Solo información relevante — el mockup se ve sobrecargado, simplificar
- Organizar por pestañas, igual que ya está hoy (`workplace_results.html` ya tiene tabs Categoría/Dominio/Dimensión — reutilizar ese patrón)
- Mantener el listado de empleados abajo tal como está hoy, solo mejorar acomodo y selección de datos mostrados
- **Orden de prioridad confirmado:** primero corregir errores (Fase 1, incluyendo activar Stripe con llaves reales — ver sección siguiente), antes de avanzar con este rediseño.

## 6. PROPUESTA (diseño): matriz visual de resultados por categoría en "Resultados completos"

**Propuesta:** rediseñar la presentación de resultados de NOM-035 con una vista tipo "Matriz de riesgos" — heatmap de nivel de riesgo (Muy alto/Alto/Medio/Bajo/Nulo) cruzado contra las 4 categorías oficiales, tarjetas resumen (nivel de riesgo predominante, % por nivel), panel de "Hallazgos clave" con lectura automática de qué combinaciones requieren atención, y pestañas adicionales (Resumen ejecutivo, Comparativo, Detalle por factor) además de la matriz. Incluye exportar y filtros.

**Verificado:** las 4 categorías mostradas en la propuesta coinciden exactamente con las categorías oficiales de la norma (Tabla 3/6 de las Guías II/III), y el backend ya calcula correctamente el nivel de riesgo por categoría (`catA`/`catB` en `surveys/views.py`, mismas tablas oficiales confirmadas en el hallazgo #3). Es decir: **esto es principalmente una mejora de presentación visual sobre datos que ya se calculan bien** — no requiere tocar la lógica de cálculo, solo la capa de presentación (la vista "Resultados completos" ya tiene los datos, solo no se muestran así hoy).

**Pendiente de decidir con Jorge:** si se prioriza, y si se integra como reemplazo de la pestaña "Categoría" ya existente en `workplace_results.html`, o como vista nueva independiente.

### 6.1 Observación adicional sobre el "Informe de Resultados" (parte del mismo mockup)
Falta agregar: **fechas** y **referencias a la NOM-035**.

**Verificado contra el numeral 7.7 de la norma** (datos obligatorios del informe de resultados): el informe debe contener, además de lo que ya aparece en el mockup (datos del centro, objetivo, actividades principales):
- **Método utilizado** conforme al numeral 7.4 (cuál guía/cuestionario se aplicó — II o III)
- **Fecha** (de elaboración/evaluación — no aparece en el encabezado del mockup)
- **Datos del responsable de la evaluación** (nombre completo y, en su caso, cédula profesional) — tampoco aparece
- Conclusiones y recomendaciones (no visibles en este recorte de pantalla, verificar si ya están más abajo en el diseño completo)

Estos son justo los campos que la observación de Jorge señala como faltantes ("fechas y referencias a la NOM-035") — coincide con los incisos d), f)-h) del numeral 7.7 que hoy no se ven en el mockup compartido.

## 7. PROPUESTA (diseño): tarjetas de planes rediseñadas — bug reportado en el prototipo

**Contexto:** mockup nuevo de tarjetas de plan (ej. "NOM-035 PyME — $1,190 MXN/anual — MÁS POPULAR"), aparentemente parte del rediseño de la página interna de Planes (no es el mismo diseño que ya integramos en la landing pública — el copy es distinto: "Cumplimiento STPS" en vez de "Guías I, II y III de la STPS").

**Bug reportado:** el botón de selección/CTA se oculta al seleccionar la tarjeta.

**Nota:** este mockup vive en la herramienta de diseño donde se está construyendo (no en este repo), así que no puedo verificarlo contra código real todavía — se queda registrado tal cual se reportó, pendiente de revisar cuando se traiga el archivo/prompt correspondiente.

## 8. Bugs reales confirmados en la página de Planes en producción (`stripe_planes.html`)

**Contexto:** a diferencia de los hallazgos #6-#7 (mockups en herramienta de diseño), estas capturas son de la página real de Planes en `normaia.ihes.mx` — sí verificadas contra el código del repo.

### 8.1 Insignia "Más popular" / "Mejor valor" aparece en los 3 planes de cada tab simultáneamente — BUG CONFIRMADO
`surveys/templates/stripe_planes.html`:
- Línea 246-247 (tab NOM-035): la condición es `plan.periodo == 'anual'` — pero **los 3 planes NOM-035 son anuales** (confirmado en `stripe_plans.py`), así que los 3 muestran la insignia "Más popular" a la vez (visible en la captura).
- Línea 276-277 (tab Psicometría): la condición es `plan.periodo == 'mensual' and plan.evaluaciones_mes == 50` — pero **ningún plan real tiene `evaluaciones_mes == 50`** (Starter=20, Ilimitado Mensual=-1/ilimitado). Esta condición nunca se cumple: la insignia nunca aparece ahí, bug opuesto (nunca se muestra en vez de mostrarse siempre).
- Línea 304-305 (tab Suite): mismo patrón que NOM-035, `plan.periodo == 'anual'` — los 3 planes Suite también son anuales, mismo bug de mostrarse en los 3 a la vez.

**Fix exacto:** el `for key, plan in planes.items` ya expone `key` (el plan_key real, ej. `nom035_empresarial`, `psico_ilimitado_mensual`, `suite_pro_100`) en las 3 tabs. Cambiar las condiciones de `plan.periodo == '...'` a comparar contra el `key` específico del plan que se quiere destacar en cada tab (consistente con lo que ya definimos en el rediseño de la landing: Empresarial en NOM-035, Ilimitado Mensual en Psicometría, Suite Pro 100 en Suite).

### 8.2 "No funciona" — botones de Stripe (Contratar / Administrar métodos de pago) — MISMA CAUSA YA CONOCIDA
Confirma que el límite de Stripe en placeholder (ver hallazgo previo sobre el error "Invalid API Key") **también bloquea estas 2 páginas reales de producción**, no solo el checkout de planes:
- Botón "Contratar" en cualquier plan de `/planes/` → error de Stripe
- Botón "Administrar métodos de pago" en Configuración → mismo error

No es un bug nuevo de código — es el mismo pendiente ya registrado desde el despliegue del VPS (activar Stripe en modo test/live). Se deja aquí solo para dejar constancia de que afecta estas 2 pantallas específicas también, por si se prioriza activar Stripe antes que las demás correcciones de este documento.

## PENDIENTE: más observaciones por llegar (Jorge sigue enviando antes de armar el prompt final para Replit)

Jorge las irá pasando conforme los socios se las compartan. Se agregan aquí mismo conforme lleguen, verificadas contra el código antes de anotarlas como "confirmado" o "por verificar".
