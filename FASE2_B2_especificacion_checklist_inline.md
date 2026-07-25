# Fase 2-B (v2) — Checklist con selector inline, sin navegar a otra pantalla

## ⚠️ Contexto: esto modifica código YA DESPLEGADO en producción (VPS)
Fase 2-B (checklist de estado, migración 0041) ya está en `main` y desplegada en `https://normaia.ihes.mx`. Jorge probó visualmente y pidió un cambio de UX: los 6 ítems que dependen del usuario tenían un botón "Abrir" que llevaba a otra pantalla solo para seleccionar un radio button — poco amigable. Este lote reemplaza eso por un selector inline + botón "Guardar estado" en la misma tarjeta, sin navegar a otra página. También cambia el set de estados posibles (ver abajo). Es un lote de ajuste sobre Fase 2-B, no de Fase 2-A ni 2-C.

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase2-b2-checklist-inline`
- `surveys/views.py` y `surveys/models.py` usan TABS. `surveys/forms.py` usa 4 ESPACIOS. `surveys/templates/*.html` es HTML/JS, sin regla de indentación Python.
- Migración manual nueva: `0042_evidencia_fase_c_estados_reetiquetados.py`, dependencia `0041_evidencia_fase_c_estado`. NO usar `makemigrations` real.
- `python -m py_compile surveys/views.py surveys/models.py surveys/forms.py` + el archivo de migración nuevo, antes de cualquier commit.

## Decisión de producto (ya confirmada con Jorge, verificada contra la norma — no volver a preguntar)

Los 6 ítems dejan de compartir un único set de 3 estados (Tienen/Trabajando/Falta). Ahora hay 2 grupos:

**Grupo A — siempre obligatorios por la norma, sin "No aplica" (2 estados: En proceso / Completado):**
- Evidencia de Difusión (`difusion`, numeral 5.7 a) — obligación incondicional
- Registros de resultados y medidas de control (`registros`, numeral 5.8) — obligación incondicional
- Mecanismos de queja/denuncia de violencia laboral (`mecanismos_queja`, numeral 8.1 b) — obligación incondicional
- Exámenes Médicos/Evaluaciones Psicológicas (`examen_medico`) — la norma SÍ lo condiciona (numeral 5.6), pero esa condición ya la calcula el sistema automáticamente (`requiere_intervencion`, sin cambios); una vez que la fila SÍ aparece (el sistema ya determinó que aplica), no se le da al usuario la opción de auto-eximirse con "No aplica"
- Medidas de Control/Programa de Intervención (`medida_control`) — mismo criterio que el anterior (numeral 5.4/8.3/8.4)

**Grupo B — condicionado a un evento real, con "No aplica" legítimo (3 estados: En proceso / Completado / No aplica):**
- Canalizaciones Guía I (`canalizacion`, numeral 5.5) — solo aplica si hubo trabajadores con acontecimientos traumáticos severos identificados; el sistema no calcula esto automáticamente hoy, por eso es el usuario quien puede marcarlo "No aplica"

**Regla de negocio importante**: nunca se debe permitir "No aplica" en un ítem del Grupo A — permitirlo dejaría que el usuario se auto-exima de una obligación que la norma no condiciona. Esta restricción se aplica tanto en el frontend (qué opciones muestra el `<select>`) como en el backend (el endpoint de guardado debe rechazar `estado=no_aplica` si el tipo no es `canalizacion`, sin confiar en que el frontend ya filtró las opciones).

**"No aplica" se excluye del cálculo del % de cumplimiento** (ni cuenta como completo ni como pendiente, igual que ya pasa hoy con los 2 ítems condicionales cuando el sistema determina que no aplican).

## Cambios requeridos

### 1. surveys/models.py — `EvidenciaFaseC` (líneas 1008-1026 actuales)

Reemplazar `ESTADO_CHOICES` y el `default`:
```python
	ESTADO_CHOICES = (
		('en_proceso', 'En proceso'),
		('completado', 'Completado'),
		('no_aplica', 'No aplica'),
	)
	TIPOS_PERMITE_NO_APLICA = ('canalizacion',)
```
(reemplaza el comentario de la línea 1022 sobre `ESTADO_CHOICES_BINARIO`, que ya no aplica — ese concepto de "binario" se elimina, ver forms.py/views.py abajo).

Cambiar la línea 1025: `estado=models.CharField(u'Estado', max_length=20, choices=ESTADO_CHOICES, default='en_proceso')`.

### 2. Migración `surveys/migrations/0042_evidencia_fase_c_estados_reetiquetados.py`

```python
from django.db import migrations, models


def remapear_estados(apps, schema_editor):
	EvidenciaFaseC = apps.get_model('surveys', 'EvidenciaFaseC')
	EvidenciaFaseC.objects.filter(estado='tienen').update(estado='completado')
	EvidenciaFaseC.objects.filter(estado__in=['trabajando', 'falta']).update(estado='en_proceso')


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0041_evidencia_fase_c_estado'),
	]

	operations = [
		migrations.RunPython(remapear_estados, migrations.RunPython.noop),
		migrations.AlterField(
			model_name='evidenciafasec',
			name='estado',
			field=models.CharField(choices=[('en_proceso', 'En proceso'), ('completado', 'Completado'), ('no_aplica', 'No aplica')], default='en_proceso', max_length=20, verbose_name='Estado'),
		),
	]
```
Esta migración SÍ preserva datos reales (a diferencia de la 0041, que borraba todo porque solo había datos de prueba) — ahora que Fase 2-B está en producción, puede haber estados reales capturados por el equipo de Jorge entre el deploy de 2-B y este cambio. `remapear_estados` traduce los valores viejos a los nuevos antes de que el `AlterField` cambie el `choices`/`default` (Django no valida `choices` a nivel de base de datos, así que el orden entre el `RunPython` y el `AlterField` no es estrictamente crítico para que la migración corra, pero mantener el remapeo primero es más claro de leer).

### 3. surveys/forms.py — `EvidenciaEstadoForm` (líneas 44-55 actuales)

```python
class EvidenciaEstadoForm(forms.Form):
    _cls = {'class': 'form-control'}
    estado = forms.ChoiceField(label='Estado', widget=forms.RadioSelect)
    notas = forms.CharField(label='Notas', required=False, widget=forms.Textarea(attrs=_cls))

    def __init__(self, *args, permite_no_aplica=False, **kwargs):
        super().__init__(*args, **kwargs)
        from surveys.models import EvidenciaFaseC
        choices = list(EvidenciaFaseC.ESTADO_CHOICES)
        if not permite_no_aplica:
            choices = [c for c in choices if c[0] != 'no_aplica']
        self.fields['estado'].choices = choices
```
Reemplaza el parámetro `binario` (y su lógica de `[('tienen', 'Realizado'), ('falta', 'No realizado')]`) por `permite_no_aplica`, que ahora filtra "No aplica" en vez de construir un set de opciones completamente distinto — ya no hay un caso "binario" separado, el Grupo A simplemente no ofrece la tercera opción.

### 4. surveys/views.py — `SubirEvidenciaFaseCView` (líneas 935-969 actuales)

Reemplazar `TIPOS_BINARIOS = ('registros', 'mecanismos_queja')` (línea 938) por:
```python
	TIPOS_PERMITE_NO_APLICA = ('canalizacion',)
```
Y en `get()` (línea 945) y `post()` (línea 958), reemplazar `binario = tipo in self.TIPOS_BINARIOS` por `permite_no_aplica = tipo in self.TIPOS_PERMITE_NO_APLICA`, pasando `permite_no_aplica=permite_no_aplica` al `EvidenciaEstadoForm(...)` en vez de `binario=binario`. Esta vista/página standalone ya no se enlaza desde el checklist (ver punto 6), pero se deja funcional por si se accede a la URL directamente — debe seguir validando correctamente.

### 5. surveys/views.py — nuevo endpoint AJAX `guardar_estado_evidencia` (agregar después de `SubirEvidenciaFaseCView`, antes de `get_portafolio_status`)

```python
@login_required
def guardar_estado_evidencia(request, workplace_id, tipo):
	if request.method != 'POST':
		return JsonResponse({'error': 'method_not_allowed'}, status=405)
	workplace = Workplace.objects.filter(id=workplace_id, user_id=request.user.id).first()
	if not workplace:
		return JsonResponse({'error': 'not_found'}, status=404)
	estado = request.POST.get('estado')
	permite_no_aplica = tipo in SubirEvidenciaFaseCView.TIPOS_PERMITE_NO_APLICA
	choices_validas = [c[0] for c in EvidenciaFaseC.ESTADO_CHOICES if permite_no_aplica or c[0] != 'no_aplica']
	if estado not in choices_validas:
		return JsonResponse({'error': 'estado_invalido'}, status=400)
	if tipo not in dict(EvidenciaFaseC.TIPO_CHOICES):
		return JsonResponse({'error': 'tipo_invalido'}, status=400)
	EvidenciaFaseC.objects.update_or_create(
		workplace=workplace, tipo=tipo,
		defaults={'estado': estado},
	)
	return JsonResponse({'ok': True})
```
**Importante**: la validación de `estado_invalido` es la que hace cumplir en el servidor la regla de negocio de "nunca permitir No aplica en el Grupo A" — no basta con que el frontend no muestre esa opción, un usuario podría mandar la petición directo. No confiar únicamente en el `<select>` del HTML.

### 6. nom035/urls.py — registrar la nueva ruta

Agregar junto a la línea de `subir_evidencia_fase_c` (línea 97 actual, `path('subir_evidencia_fase_c/<int:workplace_id>/<str:tipo>/', SubirEvidenciaFaseCView.as_view(), name='subir_evidencia_fase_c'),`):
```python
path('guardar_estado_evidencia/<int:workplace_id>/<str:tipo>/', guardar_estado_evidencia, name='guardar_estado_evidencia'),
```

### 7. surveys/views.py — reescribir `get_portafolio_status` (líneas 970-1082 actuales)

Objetivo: (a) reordenar los ítems para que salgan agrupados como Grupo A (siempre obligatorios) → Grupo B (condicionado, con No aplica) → los 2 automáticos condicionales, (b) agregar los campos nuevos que el frontend necesita para renderizar el selector inline, (c) excluir "No aplica" del cálculo del %.

Mantener sin cambios los bloques de los 3 ítems del sistema (Política de Prevención, Informe de Resultados, Cuestionarios Aplicados — líneas 978-1021 actuales), pero agregarles `'control': 'sistema'` a cada dict de `items.append({...})`.

Reemplazar TODO el bloque desde el comentario `# 4. Canalizacion Guia I` (línea 1022 actual) hasta el `return` (línea 1082 actual) por:

```python
	def _item_checklist(tipo, nombre, permite_no_aplica=False):
		ev = EvidenciaFaseC.objects.filter(workplace=workplace, tipo=tipo).first()
		estado_valor = ev.estado if ev else 'en_proceso'
		if estado_valor == 'completado':
			estado_badge = 'completo'
		elif estado_valor == 'no_aplica':
			estado_badge = 'no_aplica'
		else:
			estado_badge = 'pendiente'
		return {
			'nombre': nombre,
			'estado': estado_badge,
			'estado_valor': estado_valor,
			'control': 'checklist',
			'tipo': tipo,
			'permite_no_aplica': permite_no_aplica,
			'detalle': ev.get_estado_display() if ev else 'Sin estado registrado',
			'url': '/subir_evidencia_fase_c/' + str(workplace.id) + '/' + tipo + '/',
		}

	# Grupo A: siempre obligatorios, sin "No aplica"
	items.append(_item_checklist('difusion', 'Evidencia de Difusion'))
	items.append(_item_checklist('registros', 'Registros de resultados y medidas de control'))
	items.append(_item_checklist('mecanismos_queja', 'Mecanismos de queja/denuncia de violencia laboral'))

	# Grupo B: condicionado a un evento real, con "No aplica"
	items.append(_item_checklist('canalizacion', 'Canalizaciones Guia I', permite_no_aplica=True))

	# Automaticos: solo aparecen si el diagnostico muestra nivel Medio/Alto/Muy alto en alguna dimension
	requiere_intervencion = False
	if chart_data.get('status') == 'ok':
		for item in chart_data.get('total_dim', []):
			idx, nivel, val = item['value']
			if nivel >= 2 and val > 0:
				requiere_intervencion = True
				break
	if requiere_intervencion:
		items.append(_item_checklist('examen_medico', 'Examenes Medicos/Evaluaciones Psicologicas'))
		items.append(_item_checklist('medida_control', 'Medidas de Control/Programa de Intervencion'))

	items_contables = [i for i in items if i['estado'] != 'no_aplica']
	completos = sum(1 for i in items_contables if i['estado'] == 'completo')
	porcentaje_cumplimiento = round((completos / len(items_contables)) * 100) if items_contables else 0
	return JsonResponse({'items': items, 'porcentaje_cumplimiento': porcentaje_cumplimiento, 'completos': completos, 'total': len(items_contables)})
```

Nota: la función interna `_item_checklist` se define dentro de `get_portafolio_status` (cierra sobre `workplace`) para no repetir 6 veces el mismo patrón de `EvidenciaFaseC.objects.filter(...).first()` + armar el dict — es una simplificación válida, no un cambio de comportamiento. Los 3 ítems del sistema (política/informe/cuestionarios) NO pasan por esta función, se quedan con su lógica actual sin tocar, solo agregándoles `'control': 'sistema'`.

`'total'` en la respuesta ahora refleja `len(items_contables)` (excluyendo "No aplica"), no `len(items)` — coherente con que el % ya excluye esos ítems del cálculo.

### 8. surveys/templates/evidence.html — CSS (agregar junto al bloque `.checklist-item` existente, líneas ~91-128)

Agregar reglas nuevas para el selector inline y el badge "No aplica", además de convertir `.checklist-item` a un layout de grid para que las filas queden alineadas (título | selector | botón) en vez de flex con ancho variable:

```css
.checklist-item { display: grid; grid-template-columns: 1fr 172px 128px; align-items: center; gap: 14px; }
.checklist-item.is-na { border-left-color: #94a3b8; }
.checklist-item.is-na .checklist-status-badge { background: #f1f5f9; color: #475569; }
.checklist-item.is-na .checklist-pill { background: #f1f5f9; color: #475569; }
.checklist-state-select {
  appearance: none; -webkit-appearance: none; width: 100%;
  border: 1px solid var(--border); border-radius: var(--radius-md);
  padding: 8px 32px 8px 12px; font-size: 12.5px; font-weight: 600; color: var(--text-primary);
  background: var(--bg-base) url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="%23475569" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>') no-repeat right 10px center;
  cursor: pointer;
}
.checklist-state-select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79,70,229,.12); }
.checklist-save-btn { width: 100%; }
.checklist-save-btn[disabled] { opacity: .45; cursor: not-allowed; }
.checklist-col-placeholder { font-size: 11px; color: var(--text-muted); font-style: italic; }
.checklist-instruction-banner {
  display: flex; gap: 12px; align-items: flex-start;
  background: #eef2ff; border: 1px solid #c7d2fe;
  border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 16px;
}
.checklist-instruction-banner svg { width: 20px; height: 20px; color: #4338ca; flex-shrink: 0; margin-top: 1px; }
.checklist-instruction-banner p { margin: 0; font-size: 13px; color: #4338ca; line-height: 1.55; }
```
El ancho de columnas (`172px`/`128px`) puede ajustarse levemente si al probar visualmente no da suficiente espacio para "Exámenes Médicos/Evaluaciones Psicológicas" en la primera columna en pantallas angostas — usar buen criterio, la instrucción no es sagrada, el objetivo es que TODAS las filas (incluida la de "Política de Prevención" con su botón "Abrir") compartan las mismas 3 columnas para quedar alineadas verticalmente.

### 9. surveys/templates/evidence.html — HTML (reemplazar el bloque del checklist, líneas ~289-311 actuales)

Agregar el banner de instrucción ANTES de `<p class="checklist-section-label" v-if="workplace">Documentos requeridos</p>`:
```html
<div class="checklist-instruction-banner" v-if="workplace">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
  <p>Para cada entregable que ya tengas listo, selecciona <strong>"Completado"</strong> en el menu correspondiente y haz clic en <strong>Guardar estado</strong>. Si aun lo estas preparando, marca <strong>"En proceso"</strong>. Esto actualiza tu porcentaje de cumplimiento documental al instante.</p>
</div>
```

Reemplazar el `v-for` del checklist (línea ~291-311) para bifurcar entre ítems de sistema (mantener el `<a>` "Abrir" actual tal cual) e ítems de checklist (selector + botón, sin `<a>`):

```html
<div class="checklist-item" :class="{ 'is-complete': item.estado === 'completo', 'is-na': item.estado === 'no_aplica' }" v-for="item in portafolio_status" v-if="workplace">
  <div class="checklist-item-left">
    <div class="checklist-status-badge">
      <span v-if="item.estado === 'completo'">&#10003;</span>
      <span v-else-if="item.estado === 'no_aplica'">&#8211;</span>
      <span v-else>&#9888;</span>
    </div>
    <div class="checklist-item-info">
      <p class="checklist-item-title">
        ${item.nombre}
        <span class="checklist-pill" v-if="item.estado === 'completo'">Completo</span>
        <span class="checklist-pill" v-else-if="item.estado === 'no_aplica'">No aplica</span>
        <span class="checklist-pill" v-else>Pendiente</span>
      </p>
      <p class="checklist-item-meta">${item.detalle}</p>
    </div>
  </div>
  <template v-if="item.control === 'checklist'">
    <select class="checklist-state-select" v-model="item.estado_valor">
      <option value="en_proceso">En proceso</option>
      <option value="completado">Completado</option>
      <option value="no_aplica" v-if="item.permite_no_aplica">No aplica</option>
    </select>
    <button
      class="btn btn-primary checklist-save-btn"
      type="button"
      :disabled="item.estado_valor === item.estado_guardado"
      @click="guardarEstadoChecklist(item)"
    >Guardar estado</button>
  </template>
  <template v-else>
    <span class="checklist-col-placeholder">(automatico)</span>
    <a :href="item.url" target="_blank" class="btn checklist-save-btn">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
      Abrir
    </a>
  </template>
</div>
```
`item.estado_guardado` es un campo que NO viene del backend — se agrega en el frontend (ver punto 10) para poder comparar contra `item.estado_valor` y saber si hay cambios sin guardar (deshabilita el botón cuando no los hay, igual que en el mockup aprobado).

### 10. surveys/templates/evidence.html — JS (dentro de `methods`, junto a `get_portafolio_status()`)

Modificar `get_portafolio_status()` (línea ~478-489 actuales) para que, al recibir la respuesta, le agregue `estado_guardado` a cada ítem de tipo `checklist` (snapshot del valor recién cargado del servidor):
```javascript
      get_portafolio_status(){
        var dis=this;
        if(!dis.workplace){ return; }
        $.ajax({
            url: "{% url 'get_portafolio_status' %}",
            data: {'workplace_id': dis.workplace},
            dataType: 'json',
            success: function(data){
              data.items.forEach(function(item){
                if (item.control === 'checklist') {
                  item.estado_guardado = item.estado_valor;
                }
              });
              dis.portafolio_status = data.items;
              dis.cumplimiento_pct = data.porcentaje_cumplimiento || 0;
            }
        });
      },
```
(Ajustar al patrón exacto ya existente en el archivo — el fragmento de arriba es ilustrativo del cambio, no necesariamente línea por línea idéntico al original; conservar cualquier lógica adicional que ya tenga ese método que no se mencione aquí.)

Agregar el nuevo método `guardarEstadoChecklist`:
```javascript
      guardarEstadoChecklist(item){
        var dis=this;
        $.ajax({
          type: 'POST',
          url: '/guardar_estado_evidencia/' + dis.workplace + '/' + item.tipo + '/',
          data: {'estado': item.estado_valor},
          dataType: 'json',
          success: function(resp){
            if (resp.ok) {
              dis.get_portafolio_status();
            }
          },
          error: function(){
            alert('No se pudo guardar el estado, intenta de nuevo.');
          }
        });
      },
```
No hace falta `{% url %}` aquí porque `guardar_estado_evidencia` no está en el contexto de un `<script>` que Django procese como template en esa línea si se arma la URL por concatenación — usar buen criterio: si el archivo ya usa `{% url %}` dentro de bloques `<script>` en otras partes (sí lo hace, ver `get_portafolio_status`), es preferible usar `"{% url 'guardar_estado_evidencia' workplace_id=0 tipo='_' %}".replace('0', dis.workplace).replace('_', item.tipo)` NO — eso es frágil. Más simple y ya usado en el proyecto: la URL se puede armar por concatenación directa de string igual que ya hacen `'url'` dentro de `get_portafolio_status` en el backend (ej. `'/subir_evidencia_fase_c/' + str(workplace.id) + '/' + tipo + '/'`) — seguir ese mismo patrón en el JS, tal como está arriba, es consistente con el resto del archivo.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py surveys/models.py surveys/forms.py surveys/migrations/0042_evidencia_fase_c_estados_reetiquetados.py` sin errores.
2. Aplicar la migración 0042 en un entorno de prueba y confirmar que registros existentes con estado `tienen`/`trabajando`/`falta` (si los hay) quedan remapeados correctamente a `completado`/`en_proceso`/`en_proceso`.
3. En `/evidence/`, con un centro de prueba:
   - Los 3 ítems de sistema (Política, Informe, Cuestionarios) siguen con su botón "Abrir", sin selector.
   - Difusión, Registros, Mecanismos de queja: selector con SOLO 2 opciones (En proceso/Completado), nunca "No aplica".
   - Canalizaciones Guía I: selector con 3 opciones, incluye "No aplica".
   - Si el diagnóstico requiere intervención: Exámenes Médicos y Medidas de Control aparecen con selector de 2 opciones (sin "No aplica").
   - Cambiar el selector de un ítem → el botón "Guardar estado" se habilita; antes de tocarlo, está deshabilitado.
   - Clic en "Guardar estado" → AJAX sin recargar la página, el checklist se refresca, el % se recalcula, el botón vuelve a deshabilitarse.
   - Marcar "No aplica" en Canalizaciones → el ítem se excluye del cálculo del % (verificar contando manualmente contra `completos`/`total` de la respuesta JSON).
   - Intentar mandar `estado=no_aplica` directo por POST a `/guardar_estado_evidencia/<id>/difusion/` (con curl o la consola del navegador) → debe responder 400, no debe guardarse.
4. Confirmar que la vista standalone `/subir_evidencia_fase_c/<id>/canalizacion/` (accedida por URL directa, ya no enlazada desde el checklist) sigue funcionando y respeta la misma restricción de "No aplica" según el tipo.
5. Todas las filas del checklist (incluida la de "Política de Prevención") deben verse alineadas en columnas, sin importar el largo del nombre del entregable — revisar visualmente en desktop y en una ventana angosta.

## Fuera de alcance de este lote (no tocar)
- Fase 2-A (Riesgo General) y Fase 2-C (badges/enlaces en ficha de detalle) — lotes separados, no relacionados.
- El endpoint `get_riesgo_general` — sin cambios.
- Cualquier cambio a `ResultFiles`/`add_evidence` — no relacionado.
- Eliminar o modificar la plantilla `evidencia_fase_c_form.html` / la vista `SubirEvidenciaFaseCView` más allá del cambio puntual del punto 4 — se mantienen funcionales como fallback, no se borran.
