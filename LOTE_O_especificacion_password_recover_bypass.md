# Lote O — SEC-006: bypass total de autenticación en PasswordRecover

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-o-password-recover-bypass
- Entorno: usar el venv existente
- `surveys/views.py` usa TABS para indentación (confirmado con `cat -A` en la clase `PasswordRecover`, líneas 713-786) — respetar el estilo exacto.
- No requiere migración de base de datos.
- **Este es el hallazgo de severidad CRÍTICA más grave de toda la auditoría.** Requiere especial cuidado: el fix debe cerrar el bypass sin romper el flujo legítimo de recuperación de contraseña (que sigue siendo la única función de este endpoint).

## Contexto y confirmación del hallazgo

`PasswordRecover` (`surveys/views.py`, línea 713) es una vista **pública** (sin `LoginRequiredMixin`, endpoint intencionalmente accesible sin sesión) con 2 rutas (`nom035/urls.py` líneas 67-68):
- `path('password_recover/<str:code>/<str:iv>', PasswordRecover.as_view())` — cuando el usuario llega desde el link emailado
- `path('password_recover', PasswordRecover.as_view(), name='password_recover')` — la página base, sin código

### Flujo legítimo (correcto, no tocar)
1. Usuario pide recuperación con su email → `post()`, rama `if email!="":` → genera `verification_code, iv = encript(f"{user.id}<->{timestamp_ahora}<->{timestamp_creacion_cuenta}")`, lo manda por correo como link a `/password_recover/<code>/<iv>`
2. Usuario abre el link → `get()`, rama `if 'code' in kwargs and 'iv' in kwargs:` → desencripta, valida que no hayan pasado más de 1 hora (`timedelta(hours=1)`) y que el usuario exista → si es válido, `ctx["valid_code"]=True`, `ctx["email"]`, `ctx["name"]`
3. El template `password_recover.html` (línea 90-114), cuando `valid_code==True`, muestra el formulario para escribir la contraseña nueva

### El bug (confirmado, línea 766-786)
```python
elif "new_password1" in request.POST and "new_password1" in request.POST and "user-email" in request.POST:
    email=request.POST.get('user-email','')
    if email!="":
        user=User.objects.filter(username=email).last()
        if user:
            form =SetPasswordForm(user,request.POST)
            if form.is_valid():
                f=form.save()
                messages.success(request, "password_recovered")
```
Este bloque cambia la contraseña usando **únicamente** el email que viaja en el campo oculto `user-email` del formulario (`password_recover.html` línea 96: `<input type="hidden" name="user-email" value="{{email}}">`) — **nunca revalida el `code`/`iv`**. La variable `valid_code` calculada en el `get()` es puramente decorativa: solo controla qué se le muestra al usuario en pantalla, no viaja como parte de la petición POST ni se vuelve a verificar.

**Confirmado explotable**: un POST directo a `/password_recover` (o a `/password_recover/cualquier-cosa/cualquier-cosa`, el código/iv de la URL ni siquiera se leen en el `post()` actual) con `new_password1`, `new_password2` y `user-email=<email de la víctima>` cambia la contraseña de cualquier cuenta. No requiere sesión iniciada, no requiere el código de verificación, no requiere acceso al correo de la víctima, y no depende de si SMTP está configurado (el ataque no pasa por el flujo de correo en absoluto).

### Detalle clave que simplifica el fix: el código YA viaja en la URL de la petición POST
El `<form method="POST">` de la pestaña de cambio de contraseña (línea 92 de `password_recover.html`) **no tiene atributo `action`** — por especificación HTML, esto hace que el formulario se someta a la URL actual del documento. Como esta rama del formulario solo se renderiza cuando `valid_code==True`, lo cual solo ocurre cuando la página se cargó en `/password_recover/<code>/<iv>` (la única URL que popula `kwargs['code']`/`kwargs['iv']` en el `get()`), el POST que dispara este formulario **también aterriza en `/password_recover/<code>/<iv>`**, y Django ya captura `code`/`iv` como `**kwargs` en `post(self, request, *args, **kwargs)` — exactamente igual que en `get()`.

**Esto significa que el fix NO requiere tocar el template `password_recover.html` en absoluto** — el código/iv ya está disponible en `post()` vía `kwargs`, simplemente el código actual lo ignora. El fix es puramente revalidar en `post()` lo mismo que ya se valida en `get()`.

## Cambio requerido

### surveys/views.py — `PasswordRecover.post()` (líneas ~766-786)

Reemplazar la rama `elif "new_password1" in request.POST and "new_password1" in request.POST and "user-email" in request.POST:` por una que:

1. Corrija el typo existente que nunca comprobaba `new_password2` (la condición actual repite `"new_password1"` dos veces) — debe comprobar `"new_password1" in request.POST and "new_password2" in request.POST`
2. Exija que `'code' in kwargs and 'iv' in kwargs` (si faltan, la petición no trae un código de recuperación válido en la URL — rechazar, mismo patrón que usa `get()` para decidir si mostrar el formulario)
3. Revalide el código EXACTAMENTE con la misma lógica ya usada en `get()` (líneas 720-734): desencriptar con `decript()`, partir el texto por `'<->'`, confirmar que no pasó más de 1 hora (`timedelta(hours=1)`) desde que se generó, y que exista un `Userapp` con ese `user_id` y ese `record_create` exacto (`data[0]`, `data[2]`)
4. **Derivar el usuario a modificar desde el resultado de la desencriptación (`data[0]`), NO desde `request.POST.get('user-email')`** — el campo `user-email` del formulario no debe usarse como fuente de verdad para identificar a qué cuenta se le cambia la contraseña, precisamente porque es un valor que el cliente controla. Si se quiere, puede seguir leyéndose para logging/mensajes, pero la variable `user` que se le pasa a `SetPasswordForm(user, request.POST)` debe ser la que salga del código desencriptado y validado
5. Si el código es inválido, expiró, o no corresponde a ningún usuario: NO llamar a `SetPasswordForm`, NO cambiar ninguna contraseña, responder con `messages.success(request, "error_changing_pass")` (mismo patrón de mensaje que ya usa el código actual para el caso de error) y `ct["send_mail"]=False`
6. Si el código es válido: proceder exactamente igual que antes (`form=SetPasswordForm(user,request.POST)`, `form.is_valid()`, `form.save()`, mensajes `"password_recovered"` / `"form_error"`)

Envolver la desencriptación en `try/except` (igual que `get()`), ya que un `code`/`iv` malformado o forjado puede lanzar excepciones de padding/decodificación de AES — deben tratarse como código inválido, no como error 500.

### No tocar
- `surveys/templates/password_recover.html` — no requiere ningún cambio (ver justificación arriba)
- La rama `if email!="":` (solicitud del link por correo) — sin cambios
- `EmailVerification` (clase similar pero para verificación de correo, no de recuperación de contraseña) — mismo patrón potencialmente, pero está FUERA de alcance de este lote (no cambia contraseñas, es de menor severidad; se puede evaluar en un lote aparte si se decide)
- `encript()`/`decript()` — sin cambios, ya usan `settings.AES_ENCRYPTION_KEY` desde el Lote D

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py` sin errores
2. **Prueba del ataque original (debe fallar ahora)**: POST directo a `/password_recover` (sin code/iv en la URL) con `new_password1`, `new_password2`, `user-email=<email de una cuenta de prueba existente>` → la contraseña NO debe cambiar, confirmar iniciando sesión después con la contraseña vieja (sigue funcionando) y confirmar que la nueva NO funciona
3. **Prueba del ataque con code/iv forjados**: POST a `/password_recover/AAAA/BBBB` (valores inventados, no un código real) con los mismos campos → la contraseña NO debe cambiar, y la petición no debe devolver 500 (debe manejar el error de desencriptación con gracia)
4. **Prueba del flujo legítimo completo (no debe romperse)**: solicitar recuperación con el email de una cuenta de prueba real → confirmar que se genera el código → abrir `/password_recover/<code real>/<iv real>` dentro de la primera hora → confirmar que se muestra el formulario de cambio de contraseña → enviarlo con una contraseña nueva → confirmar que la contraseña SÍ cambia esta vez, y que se puede iniciar sesión con la contraseña nueva
5. **Prueba de expiración**: si es posible simular o esperar (o revisar por código que la lógica de `timedelta(hours=1)` se está aplicando igual que en `get()`), confirmar que un código de más de 1 hora de antigüedad es rechazado en el POST igual que ya lo es en el GET

## Fuera de alcance de este lote (no tocar)
- `EmailVerification` (verificación de correo) — patrón similar pero menor severidad, no cambia contraseñas, se evalúa aparte si se decide
- Invalidar el código después de un solo uso (hoy es reutilizable dentro de la ventana de 1 hora) — mejora recomendada a futuro, pero no es el bypass crítico que reporta SEC-006, se deja fuera para no ampliar el alcance de este lote
- INFRA-001, PN-01 a 06 — pendientes aparte
