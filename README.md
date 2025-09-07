# TP: Implementación de un Chat Básico Cliente-Servidor con Sockets y SQLite (Python)

## Objetivo
- Servidor en `localhost:5000` que recibe mensajes de clientes, los guarda en SQLite y responde con confirmación.
- Cliente que envía múltiples mensajes hasta que el usuario escriba **"éxito"**.
- Buenas prácticas de **modularización**, **comentarios** y **manejo de errores**.

## Estructura
server.py      # Servidor con sockets y SQLite (Comentar mas claro))
client.py      # Cliente interactivo por consola
mensajes.db    # (se crea automáticamente al iniciar el servidor)


## Requisitos
- Python 3.8+ (probado con 3.10+)
- No requiere dependencias externas (usa `socket` y `sqlite3` de la librería estandar).

## Cómo ejecutar (pruebas locales)
1. **Abrí una terminal** en la carpeta del proyecto y arrancá el servidor:
   bash
   python3 server.py
   

2. **Abrí otra terminal** en la misma carpeta y ejecutá el cliente:
   bash
   python3 client.py
   

3. Escribí mensajes en el cliente. El servidor guardará cada uno en la base de datos y responderá:

   [SERVIDOR] Mensaje recibido: 2025-09-07T12:00:00
   

4. Para finalizar el cliente, escribi:
   
   éxito
   
   Para detener el servidor, usá `Ctrl + C` en su terminal.

## Ver los mensajes guardados
Podés inspeccionar la DB `mensajes.db` con cualquier visor SQLite o desde Python:
```python
import sqlite3
conn = sqlite3.connect("mensajes.db")
for row in conn.execute("SELECT id, contenido, fecha_envio, ip_cliente FROM mensajes ORDER BY id;"):
    print(row)
conn.close()
```

## Notas de diseño
- **SO_REUSEADDR** permite reiniciar el servidor sin esperar a que el puerto se libere.
- El **timestamp** se genera en formato ISO (`YYYY-MM-DDTHH:MM:SS`).
- Se maneja explícitamente:
  - *Puerto ocupado* (error de `bind`): el servidor informa y sale con código 1.
  - *DB no accesible* (error de SQLite): se informa y sale con código 2.
  - *Fallas de INSERT*: se informa en stderr pero el servidor continúa atendiendo.
- Protocolo simple: el cliente abre una conexión por mensaje y espera la confirmación.



