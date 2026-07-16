# Lote L — Eliminación completa de Conekta y migración de "Métodos de pago"/"Mis pagos" a Stripe

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-l-conekta
- Entorno: usar el venv existente
- NO modificar migraciones 0001 ni 0010 (contienen historial de Conekta, se conservan tal cual)
- NO tocar el campo Userapp.client_id como columna de base de datos (no requiere migración, solo se deja de escribir en él desde el código)

## Contexto
Conekta era el proveedor de pagos original del sistema. Ya no se usa — Stripe es el proveedor definitivo (ya en producción para compra de planes). Se encontró una llave privada de Conekta de PRODUCCIÓN hardcodeada y funcionalmente activa en el código (`surveys/views.py`, línea ~43: `conekta.api_key = "key_qfCtN8NqwJRTTJR23wdcqA"`). No hay forma de revocarla desde el lado de Conekta (sin acceso a esa cuenta), así que la única mitigación posible es eliminar por completo el código que la usa.

Las secciones "Métodos de pago" y "Mis pagos" del menú de Configuración (`edit_profile.html`) usan hoy el flujo viejo de Conekta (tokenización de tarjeta vía JS, endpoints `AddCardList`/`PaymentList`). Deben reemplazarse por un enlace al Portal de Facturación de Stripe (`StripePortalView`, ya existe y funciona — gestiona tarjetas e historial de pagos nativamente, alojado por Stripe).

## Cambios requeridos

### 1. surveys/stripe_views.py — StripePortalView
Modificar el método `get()`: actualmente, si `userapp.stripe_customer_id` está vacío, redirige a `/payments/` (página que se va a eliminar en este mismo lote). Cambiar ese comportamiento: si no existe `stripe_customer_id`, crear el cliente en Stripe al vuelo (mismo patrón ya usado en `StripeCheckoutView`):
```python
customer = stripe.Customer.create(
    email=request.user.email,
    name=f"{request.user.first_name} {request.user.last_name}",
    metadata={'user_id': request.user.id}
)
userapp.stripe_customer_id = customer.id
userapp.save()
```
Y continuar normalmente creando la sesión del portal con ese `customer_id` recién creado. Ya NO debe existir ninguna ruta que redirija a `/payments/`.

### 2. surveys/views.py — eliminar código Conekta
Eliminar por completo:
- `import conekta` (línea ~cerca del inicio del archivo, confirmar ubicación exacta)
- `conekta.api_key = "key_qfCtN8NqwJRTTJR23wdcqA"` (línea ~43)
- La función `get_price(workplace)` (línea 145) — solo la usan las vistas que se eliminan en este lote, confirmado sin otros usos
- La clase `PaymentView` (línea 287) — renderiza `payments.html`, que también se elimina
- La clase `PaymentList` (línea 2420) — API de Conekta para checkout de compra antigua
- La clase `AddCardList` (línea 2610) — API de Conekta para tokenizar/eliminar tarjetas

### 3. nom035/urls.py — eliminar rutas obsoletas
Eliminar estas 3 líneas:
```python
path('api/payments/', PaymentList.as_view()),
path('payments/', PaymentView.as_view(), name='payments'),
path('api/addCard/', AddCardList.as_view()),
```
Ajustar también el import correspondiente si `PaymentView`, `PaymentList`, `AddCardList` se importaban explícitamente ahí (confirmar el patrón de imports usado, wildcard o explícito, y ajustar según corresponda). La ruta `stripe_portal` (`path('stripe/portal/', StripePortalView.as_view(), name='stripe_portal')`) NO se toca, ya existe y sigue igual.

### 4. surveys/templates/edit_profile.html — reemplazar ambas pestañas
**Pestaña "Métodos de pago"** (`id="account-vertical-payment"`, líneas ~319-383 aprox.): eliminar por completo el listado de tarjetas (`cards-list`, loop `{% for item in cards %}`), el botón "Agregar tarjeta" (`toggleAddCard`), y el formulario (`addCardForm`, `card-form` con los inputs `data-conekta="card[...]"`). Reemplazar todo el `settings-panel-body` de esa pestaña por una tarjeta simple con un mensaje breve (ej. "Administra tus tarjetas de forma segura directamente en Stripe") y un botón/link que apunte a `{% url 'stripe_portal' %}`.

**Pestaña "Mis pagos"** (`id="account-vertical-purchases"`): eliminar el listado de compras (`purchases-list`, loop `{% for item in purchases %}` con productos/montos de Conekta). Reemplazar por el mismo tipo de tarjeta simple con mensaje (ej. "Consulta tu historial completo de pagos y facturas en Stripe") y el mismo link a `{% url 'stripe_portal' %}`.

**Eliminar del `<script>` de este archivo:**
- `<script type="text/javascript" src="https://cdn.conekta.io/js/latest/conekta.js"></script>` (línea ~429)
- El bloque completo de `Conekta.setPublicKey(...)`, `conektaSuccessResponseHandler`, `conektaErrorResponseHandler`, y la llamada `Conekta.Token.create(...)` (líneas ~462-496)
- Cualquier handler JS asociado a `#submit-card`, `#toggleAddCard`, `.delete-card` que dependa de este flujo (quedarían huérfanos sin la sección HTML que los usa)

### 5. surveys/templates/payments.html
Eliminar el archivo por completo — depende 100% de `PaymentView`/`PaymentList`/Conekta, sin ningún otro punto del sistema que lo referencie (confirmado).

### 6. surveys/models.py
- Campo `Userapp.client_id` (línea 63): dejarlo en el modelo tal cual (no tocar, no migración), pero ya no se escribirá desde ningún lado del código tras eliminar `AddCardList`. Opcional: agregar comentario `# DEPRECATED - Conekta ya no se usa, campo se conserva por compatibilidad historica` justo arriba de la definición del campo.
- Eliminar el bloque comentado `# class ConektaWebhook(generics.GenericAPIView):` (línea 670) y las líneas comentadas que lo acompañen — es código muerto sin funcionalidad.

### 7. requirements.txt
Eliminar la línea `conekta==6.0.4`.

### 8. Modelos que NO se tocan en este lote (decisión explícita)
`PaymentCard` y `Product` quedan como están (sin migración, sin cambios) — son modelos con posible data histórica, dejar de escribir en ellos es suficiente por ahora. No se requiere limpieza de datos en este lote.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py surveys/stripe_views.py surveys/models.py nom035/urls.py` sin errores
2. Confirmar con grep que ya no queda ningún `import conekta` ni `conekta.` activo (fuera de comentarios/migraciones históricas) en surveys/views.py: `grep -n "conekta" surveys/views.py` debe devolver vacío o solo referencias en migraciones si aplica
3. En staging: iniciar sesión con una cuenta de prueba SIN stripe_customer_id previo, hacer clic en "Métodos de pago" → confirmar que crea el cliente de Stripe al vuelo y redirige correctamente al Portal (no debe caer en ningún 404 ni redirigir a /payments/)
4. Confirmar visualmente que ambas pestañas de edit_profile.html (Métodos de pago, Mis pagos) muestran el nuevo diseño simple con el botón hacia Stripe, sin ningún resto visual del formulario viejo de tarjetas
5. Confirmar que /payments/ y /api/payments/ y /api/addCard/ ya no existen (deben dar 404)

## Fuera de alcance de este lote (no tocar)
- SEC-006 (bypass de PasswordRecover) — pendiente aparte, decisión ya tomada de dejarlo para el final
- INFRA-001 (Volume persistente Railway) — infraestructura, no código
- Migraciones 0001 y 0010 — se conservan intactas
