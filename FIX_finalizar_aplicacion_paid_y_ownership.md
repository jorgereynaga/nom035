# Fix: "Finalizar aplicación" nunca se habilita + EndEvaluation sin validar dueño

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/finalizar-aplicacion-paid-y-ownership`
- `surveys/views.py` usa TABS (confirmado con `cat -A`, no usar espacios al indentar). `surveys/templates/*.html` es HTML/JS.
- No se agrega ningún modelo ni migración nueva.
- `python -m py_compile surveys/views.py` antes de cualquier commit.
- `python manage.py check` antes de cualquier commit.

## Contexto

Investigando el pendiente "`EndEvaluation` no valida completitud antes de avanzar de evaluación" (registrado en `ESTADO.md`/`SOCIOS_feedback_correcciones.md` hallazgo #9), se encontró que el problema real es más profundo: el campo `Workplace.paid` (que controla si el botón "Finalizar aplicación" está habilitado en `workplace_detail.html`) se crea siempre en `False` al dar de alta un centro de trabajo (`WorkplaceList.post()`, `surveys/views.py`), **sin distinguir centros demo de centros reales**, y **ningún código en todo el proyecto lo vuelve a poner en `True`**. Confirmado empíricamente: los centros de trabajo reales en base de datos tienen `paid=False`, y el HTML renderizado real trae el atributo `disabled` en el botón "Finalizar aplicación".

**Decisiones de producto ya confirmadas con Jorge, no volver a preguntar:**

1. Para un centro de trabajo **demo** (`es_demo=True`), `paid` debe seguir en `False` — es intencional, para que los datos de ejemplo no se puedan alterar avanzando su evaluación.
2. Para un centro de trabajo **real** (no demo), creado después de que el usuario ya tiene un plan/créditos activos (la pantalla de alta ya bloquea el acceso sin eso, ver `WorkplaceFormView.get()`), el botón "Finalizar aplicación" debe estar **habilitado desde la creación** (`paid=True`), para que el usuario pueda cerrar la aplicación de encuestas cuando él decida — sin ningún umbral de % de empleados contestados. El clic explícito del usuario en ese botón (con el modal de confirmación ya existente, que advierte "esta acción suspenderá la aplicación de encuestas...") **es** la señal de completitud que se buscaba; no se requiere ninguna validación numérica adicional.
3. Al finalizar la evaluación actual (`EndEvaluation`), la evaluación que se **cierra** (`workplace.evaluation` antes de incrementar) queda deshabilitada automáticamente porque ya no es la evaluación vigente — **no** porque `paid` se ponga en `False`. La evaluación **nueva** (`workplace.evaluation` después de incrementar) debe quedar con `paid=True` de inmediato, para que el usuario pueda finalizarla cuando él decida, igual que la anterior. Es decir: `EndEvaluation` debe dejar `workplace.paid=True` (no `False`) después de incrementar.
4. **Hallazgo de seguridad encontrado en el camino, incluir en este mismo fix**: `EndEvaluation.get()` obtiene el `Workplace` solo por `id`, sin verificar que pertenezca al usuario autenticado (`Workplace.objects.filter(id=workplace_id).last()`) — cualquier usuario autenticado podría llamar este endpoint con el `workplace_id` de otro usuario y avanzarle la evaluación. Debe agregarse el mismo patrón de ownership ya usado en el resto del proyecto desde el Lote A (ej. `WorkplaceDetailView`, línea 677 actual: `if not request.user.workplaces.filter(id=kwargs['workplace_id']).exists(): return HttpResponseRedirect(...)`).

## Cambios requeridos

### 1. `surveys/views.py` — `WorkplaceList.post()` (línea 2693-2721 actuales)

Cambiar la línea 2714 actual:

```python
		data['paid']=False
```

por:

```python
		data['paid']=True
```

(Este endpoint `POST /api/workplace/` solo se usa para el alta de centros reales desde `workplaceform.html` — los centros demo se generan aparte, vía el management command `cargar_datos_demo`, que ya construye sus propios objetos `Workplace` directamente con `paid=False` explícito y no pasa por esta vista. No hace falta ninguna condición adicional aquí.)

### 2. `surveys/views.py` — `EndEvaluation.get()` (línea 3052-3072 actuales)

Reemplazar el método completo:

```python
class EndEvaluation(APIView):
	http_method_names = ['get',]
	permission_classes = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,SessionAuthentication)
	def get(self, request, format=None):
		try:
			workplace_id=request.query_params.get('workplace_id') or request.data.get('workplace_id')
			if not request.user.workplaces.filter(id=workplace_id).exists():
				return Response({'status':'error', 'error':'Centro de trabajo no encontrado.'}, status=403)
			workplace=Workplace.objects.filter(id=workplace_id).last()
			if workplace.es_demo:
				return Response({'status':'error', 'error':'No es posible avanzar evaluacion en un centro de trabajo de demostracion.'})
			EvaluationHistory.objects.create(
				workplace=workplace,
				numero_evaluacion=workplace.evaluation,
				guia=workplace.survey_type(),
			)
			workplace.evaluation=workplace.evaluation+1
			workplace.paid=True
			workplace.save()
			return Response({'status':'ok'})
		except Exception as e:
			return Response({'status':'error', 'error':f"error::{e}"})
```

Cambios respecto al código actual: se agregó la validación de ownership al inicio (mismo patrón que `WorkplaceDetailView`), y se cambió `workplace.paid=False` por `workplace.paid=True`.

### 3. `surveys/templates/workplace_detail.html` — ajustar condición de "Ver resultados" (línea 426-437 actuales)

El bloque actual:

```html
        {% if not paid and evaluation > 1 %}
                <a href="/workplace_result/{{workplace_id}}/{{evaluation|add:"-1"}}/" class="btn btn-primary btn-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                  Ver resultados
                </a>
                {% elif paid %}
                <button class="btn btn-outline btn-sm" onclick="alert('Debes finalizar la aplicación antes de ver los resultados.')">
                  Ver resultados
                </button>
                {% else %}
                <button disabled class="btn btn-outline btn-sm">Ver resultados</button>
                {% endif %}
```

Reemplazar la condición `{% if not paid and evaluation > 1 %}` por `{% if evaluation > 1 %}` (ya que con el cambio del punto 2, `workplace.evaluation` solo se incrementa después de una finalización real vía `EndEvaluation` — el número de evaluación en sí, no `paid`, es ahora la señal correcta de "existe una evaluación anterior ya finalizada con resultados que ver"):

```html
        {% if evaluation > 1 %}
                <a href="/workplace_result/{{workplace_id}}/{{evaluation|add:"-1"}}/" class="btn btn-primary btn-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                  Ver resultados
                </a>
                {% elif paid %}
                <button class="btn btn-outline btn-sm" onclick="alert('Debes finalizar la aplicación antes de ver los resultados.')">
                  Ver resultados
                </button>
                {% else %}
                <button disabled class="btn btn-outline btn-sm">Ver resultados</button>
                {% endif %}
```

No se toca la línea 493 actual (`{% if not paid %}{{evaluation|add:"-1"}}{% else %}{{evaluation}}{% endif %}` dentro del `ajax` de la tabla de empleados) — con `paid` prácticamente siempre en `True` para centros reales tras este fix, esa tabla mostrará consistentemente los empleados de la evaluación **actual** en curso, que es el comportamiento esperado en la ficha del centro.

## Validación requerida

1. `python -m py_compile surveys/views.py`.
2. `python manage.py check`.
3. Crear un centro de trabajo real (no demo) con un usuario que tenga plan/créditos activos: confirmar que `Workplace.objects.get(id=...).paid == True` inmediatamente después de crearlo, y que el botón "Finalizar aplicación" aparece **habilitado** (sin `disabled`) al renderizar `workplace_detail.html`.
4. Confirmar que un centro **demo** (`es_demo=True`) sigue con `paid=False` y el botón sigue deshabilitado (no debe haber regresión en el comportamiento protegido de los datos de ejemplo).
5. Con el centro real del punto 3, llamar `EndEvaluation` (clic real en "Finalizar aplicación" → modal → "Aceptar", o vía test client autenticado como el dueño): confirmar que `evaluation` se incrementa, se crea el registro `EvaluationHistory` correspondiente, y `paid` queda en `True` (no `False`) después.
6. Confirmar que, tras el punto 5, "Ver resultados" de la evaluación recién cerrada está disponible (link a `evaluation-1`), y "Finalizar aplicación" sigue habilitado para la nueva evaluación en curso.
7. Probar el ownership de `EndEvaluation`: llamar el endpoint autenticado como un usuario que **no** es dueño del `workplace_id` dado — debe devolver `{'status':'error', 'error':'Centro de trabajo no encontrado.'}` con status 403, y **no** debe modificarse el `Workplace` de la víctima (verificar `evaluation`/`paid`/`EvaluationHistory` sin cambios).
8. Confirmar que llamar `EndEvaluation` sobre un centro demo sigue bloqueado con el mismo mensaje de siempre ("No es posible avanzar evaluacion en un centro de trabajo de demostracion.").
9. Prueba visual en navegador: en un centro real recién creado, "Finalizar aplicación" habilitado desde el inicio; tras finalizar, "Ver resultados" de la ronda cerrada funciona y "Finalizar aplicación" de la ronda nueva sigue habilitado. Sin errores de consola.
10. Confirmar que el alta de empleados, la carga masiva, y el resto de la ficha del centro de trabajo siguen funcionando exactamente igual (no debe haber regresión).

## Fuera de alcance

- No se modifica ningún otro endpoint ni patrón de ownership fuera de `EndEvaluation`.
- No se agrega backfill de `paid=True` para centros de trabajo reales ya existentes en base de datos con `paid=False` — no hay clientes reales todavía, no hace falta.
- No se rediseña el campo `paid` en el modelo (renombrarlo, separarlo en dos campos, etc.) — se mantiene tal cual, solo se corrige cuándo se asigna `True`/`False`.
- No se agrega ningún umbral de % de empleados contestados ni validación de completitud numérica — decisión explícita de Jorge, la finalización explícita del usuario es la única señal requerida.
