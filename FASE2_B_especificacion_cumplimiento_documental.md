# Fase 2-B — Cumplimiento documental: checklist de estado (elimina subida de archivos)

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase2-b-cumplimiento-documental`
- Entorno: usar el venv existente (Python 3.10)
- `surveys/models.py` y `surveys/views.py` usan **TABS**. `surveys/forms.py` usa **4 ESPACIOS** (confirmado con `cat -A`, distinto de models/views — respetar el estilo de cada archivo). Verificar con `cat -A` antes de insertar líneas nuevas.
- Migración manual escrita a mano, número siguiente disponible: `0041_...` (la última existente es `0040_plan_purchase_event.py`). NO usar `makemigrations` real.
- `python -m py_compile surveys/models.py surveys/views.py surveys/forms.py` antes de cualquier commit.
- **Este lote borra datos reales de la tabla `EvidenciaFaseC`** (decisión explícita de Jorge, confirmada 23 Jul 2026: no hay clientes reales en producción todavía, solo datos de prueba). Antes de correr la migración en cualquier ambiente que no sea local, confirmar con Jorge que sigue siendo así en ese momento.

## Contexto

Los socios pidieron eliminar la subida de archivos del Portafolio de Evidencias (Fase C) por el riesgo de costo de hosting a futuro — confirmado técnicamente: hoy cada evidencia se guarda como archivo físico en disco local sobre un Volume de Railway (`FileSystemStorage`, `surveys/models.py:9`), sin almacenamiento externo con costo variable, sin límite de cantidad de archivos por tipo/centro. El disco crece sin tope.

En su lugar, piden un checklist donde el usuario marca el estado de cada elemento documental (Tienen / Les falta / Lo están trabajando), mostrando un % de cumplimiento en los resultados y datos del centro de trabajo. Este SÍ es un indicador legítimo de "Cumplimiento NOM-035" (a diferencia del Riesgo General de la Fase 2-A) porque nace de documentación/acciones del Capítulo 5 de la norma, no de resultados de riesgo psicosocial.

El checklist ya existe conceptualmente hoy: `get_portafolio_status` (`surveys/views.py:962-1054`) ya arma una lista de 5-7 ítems con `estado: 'completo'/'pendiente'`, consumida por `evidence.html`. De esos, 3 ítems (Política, Informe de Resultados, Cuestionarios Aplicados) ya se calculan de datos existentes, sin archivo — no se tocan. Los otros 4 (Difusión, Canalización, Examen médico, Medida de control) hoy dependen de `EvidenciaFaseC.objects.filter(...).exists()` — es decir, de si hay al menos un archivo subido de ese tipo. Este lote cambia el criterio de esos 4, de "existe archivo" a "estado marcado por el usuario", y agrega 2 ítems nuevos que la norma exige y hoy no se rastrean en absoluto (Registros, numeral 5.8; Mecanismos de queja, numeral 8.1 inciso b).

**Decisiones ya confirmadas con Jorge (23 jul 2026), no volver a preguntar:**
1. Se elimina la subida de archivos. El campo de archivo del modelo se **comenta** (no se borra la línea del código), por si se decide revertir esta decisión más adelante.
2. Los registros existentes de `EvidenciaFaseC` (archivos de prueba en el ambiente actual) se eliminan directamente vía la migración de este lote.
3. Los 2 ítems nuevos (Registros, Mecanismos de queja) se agregan ya, con un selector de **2 estados** (Realizado / No realizado) — más simple que el de 3 estados de los demás ítems, porque son elementos binarios.

## Cambios requeridos

### 1. surveys/models.py — `EvidenciaFaseC` (líneas 1008-1021)

Reemplazar el modelo completo por:

```python
class EvidenciaFaseC(models.Model):
	TIPO_CHOICES = (
		('canalizacion', 'Canalizacion Guia I (traumas severos)'),
		('examen_medico', 'Examen medico/evaluacion psicologica'),
		('medida_control', 'Medida de control/Programa de intervencion'),
		('difusion', 'Evidencia de difusion de la politica'),
		('registros', 'Registros de resultados y medidas de control'),
		('mecanismos_queja', 'Mecanismos de queja/denuncia de violencia laboral'),
	)
	ESTADO_CHOICES = (
		('tienen', 'Tienen'),
		('trabajando', 'Lo estan trabajando'),
		('falta', 'Les falta'),
	)
	# ESTADO_CHOICES_BINARIO se usa en el form para 'registros' y 'mecanismos_queja' (solo 2 opciones, ver forms.py)
	workplace=models.ForeignKey(Workplace,related_name="evidencias_fase_c",verbose_name='Centro de trabajo', on_delete=models.CASCADE)
	tipo=models.CharField(u'Tipo de evidencia', max_length=30, choices=TIPO_CHOICES)
	estado=models.CharField(u'Estado', max_length=20, choices=ESTADO_CHOICES, default='falta')
	# archivo=models.FileField(u'Archivo', upload_to='evidencias_fase_c/%Y/%m/', storage=protected_storage)  # eliminado 2026-07 (Fase 2-B): se reemplazo por checklist de estado para evitar crecimiento de disco. Descomentar si se decide revertir.
	notas=models.TextField(u'Notas', blank=True)
	fecha_carga=models.DateTimeField(auto_now_add=True)
	fecha_actualizacion=models.DateTimeField(auto_now=True)
	class Meta:
		unique_together = ('workplace', 'tipo')
	def __str__(self):
		return f"{self.get_tipo_display()} - {self.workplace.name} - {self.get_estado_display()}"
```

Nota: `unique_together` cambia el modelo de "una fila por cada archivo subido" a "una fila por workplace+tipo, con su estado actual" — coherente con que ahora es un estado, no un historial de subidas.

### 2. Migración manual `surveys/migrations/0041_evidencia_fase_c_estado.py`

Dependencia: `0040_plan_purchase_event`. Debe hacer, en este orden:
1. `RunPython` que borre todos los registros existentes de `EvidenciaFaseC` (`EvidenciaFaseC.objects.all().delete()` dentro de una función que reciba `apps, schema_editor` y use `apps.get_model('surveys', 'EvidenciaFaseC')`, no el import directo del modelo). Función reversa: `migrations.RunPython.noop` (no se puede revertir un borrado de datos).
2. `AddField` para `estado` (`CharField`, `max_length=20`, `choices=...`, `default='falta'`).
3. `AddField` para `fecha_actualizacion` (`DateTimeField`, `auto_now=True`) — usar `auto_now_add=False` en la migración con un default temporal si Django lo exige para filas existentes (no debería aplicar, ya que el paso 1 las borró todas).
4. `AlterField` para `tipo`, actualizando `choices` para incluir `registros` y `mecanismos_queja`.
5. `AlterUniqueTogether` agregando `('workplace', 'tipo')`.

**No** incluir ninguna operación sobre el campo `archivo` (ni `RemoveField` ni `AlterField`) — el campo se queda comentado en el modelo pero la columna física permanece en la base de datos (inofensivo, no se usa). No ejecutar `makemigrations` para "corregir" esto — es intencional, sigue el patrón ya establecido del proyecto de migraciones 100% manuales.

### 3. surveys/forms.py — reemplazar `EvidenciaFaseCForm` (líneas 44-59 aprox.)

```python
class EvidenciaEstadoForm(forms.Form):
    _cls = {'class': 'form-control'}
    estado = forms.ChoiceField(label='Estado', widget=forms.RadioSelect)
    notas = forms.CharField(label='Notas', required=False, widget=forms.Textarea(attrs=_cls))

    def __init__(self, *args, binario=False, **kwargs):
        super().__init__(*args, **kwargs)
        from surveys.models import EvidenciaFaseC
        if binario:
            self.fields['estado'].choices = [('tienen', 'Realizado'), ('falta', 'No realizado')]
        else:
            self.fields['estado'].choices = EvidenciaFaseC.ESTADO_CHOICES
```

`EvidenciaFaseCForm` (la clase vieja, con `archivo`/`clean_archivo`) se **comenta por completo** en el archivo (todo el bloque de clase, no se borra), con un comentario arriba: `# Reemplazado por EvidenciaEstadoForm en Fase 2-B (2026-07). Descomentar si se revierte la eliminacion de subida de archivos.`

`binario=True` se usa para los tipos `registros` y `mecanismos_queja` (selector de 2 opciones); el resto usa las 3 opciones normales de `ESTADO_CHOICES`.

### 4. surveys/views.py — reescribir `SubirEvidenciaFaseCView` (líneas 934-961)

```python
class SubirEvidenciaFaseCView(LoginRequiredMixin,View):
	login_url = reverse_lazy('login')
	redirect_field_name = 'redirect_to'
	TIPOS_BINARIOS = ('registros', 'mecanismos_queja')
	def get(self, request, *args, **kwargs):
		workplace_id = kwargs.get('workplace_id')
		tipo = kwargs.get('tipo')
		workplace = Workplace.objects.filter(id=workplace_id, user_id=request.user.id).first()
		if not workplace:
			return HttpResponseRedirect(reverse_lazy('workplaces'))
		binario = tipo in self.TIPOS_BINARIOS
		instancia = EvidenciaFaseC.objects.filter(workplace=workplace, tipo=tipo).first()
		initial = {'estado': instancia.estado, 'notas': instancia.notas} if instancia else {}
		form = EvidenciaEstadoForm(initial=initial, binario=binario)
		tipo_display = dict(EvidenciaFaseC.TIPO_CHOICES).get(tipo, tipo)
		ctx = {'workplace': workplace, 'form': form, 'instancia': instancia, 'tipo': tipo, 'tipo_display': tipo_display}
		return render(request, 'evidencia_fase_c_form.html', ctx)
	def post(self, request, *args, **kwargs):
		workplace_id = kwargs.get('workplace_id')
		tipo = kwargs.get('tipo')
		workplace = Workplace.objects.filter(id=workplace_id, user_id=request.user.id).first()
		if not workplace:
			return HttpResponseRedirect(reverse_lazy('workplaces'))
		binario = tipo in self.TIPOS_BINARIOS
		form = EvidenciaEstadoForm(request.POST, binario=binario)
		if form.is_valid():
			EvidenciaFaseC.objects.update_or_create(
				workplace=workplace, tipo=tipo,
				defaults={'estado': form.cleaned_data['estado'], 'notas': form.cleaned_data['notas']},
			)
			return HttpResponseRedirect(reverse_lazy('subir_evidencia_fase_c', kwargs={'workplace_id': workplace.id, 'tipo': tipo}))
		instancia = EvidenciaFaseC.objects.filter(workplace=workplace, tipo=tipo).first()
		tipo_display = dict(EvidenciaFaseC.TIPO_CHOICES).get(tipo, tipo)
		ctx = {'workplace': workplace, 'form': form, 'instancia': instancia, 'tipo': tipo, 'tipo_display': tipo_display}
		return render(request, 'evidencia_fase_c_form.html', ctx)
```

Nota clave: `update_or_create` en vez del `create` anterior (línea 956 original) — ahora es "un estado actual", no "un historial de subidas".

`download_evidencia_fase_c` (`surveys/views.py:126`) y su ruta (`nom035/urls.py:101`, `descargar/evidencia/<int:evidencia_id>/`) se **comentan por completo** (función y línea de `urls.py`), con la misma nota de "reemplazado en Fase 2-B, descomentar si se revierte".

### 5. surveys/views.py — `get_portafolio_status` (líneas 962-1054)

**5.1 — Cambiar el criterio de los 4 ítems existentes que usan `EvidenciaFaseC`** (líneas 1014-1053): en vez de `.filter(workplace=workplace, tipo='...').exists()`, usar:
```python
ev = EvidenciaFaseC.objects.filter(workplace=workplace, tipo='difusion').first()
difusion_completo = ev is not None and ev.estado == 'tienen'
```
(mismo patrón para `canalizacion`, `examen_medico`, `medida_control`). El campo `detalle` de cada ítem debe reflejar el estado real, no solo completo/pendiente — ej.: `ev.get_estado_display() if ev else 'Sin estado registrado'`.

**5.2 — Agregar los 2 ítems nuevos** (después del bloque condicional de examen médico/medida de control, línea ~1053, pero estos 2 SIEMPRE aplican, no son condicionales):
```python
	registros_ev = EvidenciaFaseC.objects.filter(workplace=workplace, tipo='registros').first()
	items.append({
		'nombre': 'Registros de resultados y medidas de control',
		'estado': 'completo' if (registros_ev and registros_ev.estado == 'tienen') else 'pendiente',
		'detalle': registros_ev.get_estado_display() if registros_ev else 'Sin estado registrado',
		'url': '/subir_evidencia_fase_c/' + str(workplace.id) + '/registros/',
	})
	queja_ev = EvidenciaFaseC.objects.filter(workplace=workplace, tipo='mecanismos_queja').first()
	items.append({
		'nombre': 'Mecanismos de queja/denuncia de violencia laboral',
		'estado': 'completo' if (queja_ev and queja_ev.estado == 'tienen') else 'pendiente',
		'detalle': queja_ev.get_estado_display() if queja_ev else 'Sin estado registrado',
		'url': '/subir_evidencia_fase_c/' + str(workplace.id) + '/mecanismos_queja/',
	})
```

**5.3 — Agregar el % de cumplimiento documental al JSON de respuesta**, justo antes del `return` (línea 1054):
```python
	completos = sum(1 for i in items if i['estado'] == 'completo')
	porcentaje_cumplimiento = round((completos / len(items)) * 100) if items else 0
	return JsonResponse({'items': items, 'porcentaje_cumplimiento': porcentaje_cumplimiento, 'completos': completos, 'total': len(items)})
```
Esto no rompe el consumo actual en `evidence.html` (que solo lee `data.items`) — es un campo adicional, aditivo.

### 6. surveys/templates/evidencia_fase_c_form.html

Reemplazar la línea 52 (texto de instrucciones sobre subir archivo) por algo como: *"Marca el estado de este elemento documental. Este dato alimenta el % de cumplimiento documental del centro de trabajo."*

Eliminar por completo el bloque `{% if evidencias %}...{% endif %}` (líneas 54-66, la lista de archivos ya subidos con el link "Ver archivo") — ya no aplica, no hay archivos. El formulario (líneas 68-80) NO requiere cambios de template: como `EvidenciaEstadoForm` usa `forms.RadioSelect` para `estado`, el `{{ field }}` del loop existente ya renderiza los radios correctamente sin tocar el HTML. Cambiar el texto del botón (línea 79) de "Subir evidencia" a "Guardar estado". Quitar `enctype="multipart/form-data"` del `<form>` (línea 68) — ya no hay subida de archivo.

### 7. surveys/templates/evidence.html

**7.1** — El banner decorativo (líneas 277-286, `.compliance-banner`) hoy es puramente de texto fijo, sin ningún porcentaje. Agregar el porcentaje real: en el JS que consume `get_portafolio_status` (línea ~477-490), guardar también `porcentaje_cumplimiento` en una variable de Vue (ej. `cumplimiento_pct: 0`), y mostrarla en el banner, ej.: `<p class="compliance-banner-sub">${cumplimiento_pct}% completado — Checklist de documentos y evidencias requeridos por la norma</p>`.

**7.2** — Los botones "Abrir" de cada ítem del checklist (línea 306-309) ya apuntan a `item.url`, que sigue siendo la misma ruta `/subir_evidencia_fase_c/<workplace_id>/<tipo>/` — no requieren cambio, siguen funcionando porque la vista de destino ahora es el formulario de estado en vez de subida.

### 8. Otros lugares que referencian archivo/descarga — buscar y limpiar

Correr `grep -rn "download_evidencia_fase_c\|EvidenciaFaseCForm\b" surveys/ nom035/` después de los cambios anteriores para confirmar que no queda ninguna referencia activa (fuera de los bloques ya comentados) a la vista de descarga ni al form viejo, en ningún otro template o vista.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/models.py surveys/views.py surveys/forms.py` sin errores.
2. Confirmar que la migración `0041` aplica sin error sobre el entorno local de prueba (`python manage.py migrate`), y que después de aplicarla `EvidenciaFaseC.objects.count()` es 0.
3. Probar en navegador, con un centro de trabajo de prueba:
   - `/evidence/` muestra el checklist con 9 ítems (7 anteriores más los 2 nuevos), el banner muestra un % (0% al inicio, si no hay nada marcado).
   - Clic en "Abrir" de un ítem de 3 estados (ej. Difusión) → formulario con 3 radios, sin campo de archivo.
   - Clic en "Abrir" de un ítem binario (Registros o Mecanismos de queja) → formulario con solo 2 radios (Realizado/No realizado).
   - Marcar "Tienen"/"Realizado" en varios ítems, guardar, volver a `/evidence/` → el checklist refleja el nuevo estado y el % sube correctamente.
   - Volver a abrir el mismo ítem ya marcado → el radio correcto aparece pre-seleccionado (via `initial`).
4. Confirmar que `/subir_evidencia_fase_c/<id>/difusion/` y los demás tipos NO aceptan ni muestran ningún campo de archivo en ningún punto del flujo.
5. Confirmar que no hay ningún error 404/500 al navegar `/evidence/` de principio a fin con un usuario de prueba real.
6. Revisar visualmente que `EvidenciaFaseCForm` y `download_evidencia_fase_c` quedaron comentados (no borrados) en el código, con la nota explicativa.

## Fuera de alcance de este lote (no tocar)
- Mostrar el % de cumplimiento documental en `workplace_results.html` o `workplace_detail.html` — es una integración nueva que se puede pedir como lote separado una vez confirmado que este checklist funciona bien en `/evidence/`.
- El indicador de Riesgo General (Fase 2-A) — lote aparte, no relacionado.
- Rediseño de la lista de Centros de Trabajo con badges de cumplimiento (hallazgo 5.1 del backlog) — pendiente, no aquí.
- `ResultFiles`/`add_evidence` (subida de "resultados" generados por staff, distinta de las evidencias del cliente) — no se toca, es un modelo y flujo completamente separado.
