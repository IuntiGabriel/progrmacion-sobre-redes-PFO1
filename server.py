#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de chat básico con sockets y SQLite.
Requisitos del TP:
- Escuchar en localhost:5000
- Modularización en funciones separadas
- Guardar mensajes en DB SQLite: (id, contenido, fecha_envio, ip_cliente)
- Manejo de errores (puerto ocupado, DB no accesible)
- Responder al cliente: "Mensaje recibido: <timestamp>"
"""

import socket
import sqlite3
import datetime
import sys
from contextlib import closing

HOST = "127.0.0.1"   # localhost
PORT = 5000          # puerto de escucha
DB_PATH = "mensajes.db"

# -------------------------
# Base de Datos (sqlite3)
# -------------------------

def init_db(db_path: str) -> sqlite3.Connection:
    """
    Inicializa/abre la base de datos y crea la tabla si no existe.
    Maneja errores de acceso a la DB.
    """
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            );
        """)
        conn.commit()
        return conn
    except sqlite3.Error as e:
        # Error crítico: si la DB no es accesible, salimos con código != 0
        print(f"[ERROR] No se puede acceder a la DB '{db_path}': {e}", file=sys.stderr)
        sys.exit(2)

def guardar_mensaje(conn: sqlite3.Connection, contenido: str, fecha_envio: str, ip_cliente: str) -> None:
    """
    Inserta un mensaje en la tabla mensajes.
    """
    try:
        conn.execute(
            "INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?);",
            (contenido, fecha_envio, ip_cliente)
        )
        conn.commit()
    except sqlite3.Error as e:
        # No abortamos el servidor, pero informamos el problema.
        print(f"[ERROR] Falló INSERT en DB: {e}", file=sys.stderr)

# -------------------------
# Socket TCP/IP
# -------------------------

def inicializar_socket(host: str, port: int) -> socket.socket:
    """
    Configura el socket TCP/IP para escuchar en host:port.
    Maneja el error de puerto ocupado.
    """
    try:
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Reusar dirección/puerto rápidamente tras reinicios del servidor (buena práctica)
        srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Enlazar y escuchar
        srv_sock.bind((host, port))  # Configuración del socket TCP/IP
        srv_sock.listen(5)           # backlog: hasta 5 conexiones en espera
        print(f"[OK] Servidor escuchando en {host}:{port}")
        return srv_sock
    except OSError as e:
        # Si el puerto ya está en uso u otro problema, informamos claramente
        print(f"[ERROR] No se pudo iniciar el servidor en {host}:{port}: {e}", file=sys.stderr)
        sys.exit(1)

def responder(conn: socket.socket, mensaje: str) -> None:
    """
    Envía una respuesta codificada en UTF-8 al cliente.
    """
    conn.sendall(mensaje.encode('utf-8'))

def recibir_texto(conn: socket.socket, max_bytes: int = 4096) -> str:
    """
    Recibe un bloque de datos desde el cliente y lo decodifica como UTF-8.
    En este protocolo sencillo, el cliente envía un único mensaje y espera la respuesta.
    """
    data = conn.recv(max_bytes)
    if not data:
        return ""
    return data.decode('utf-8', errors='replace').strip()

def atender_cliente(conn: socket.socket, addr: tuple, db_conn: sqlite3.Connection) -> None:
    """
    Maneja el ciclo de atención de *una* conexión de cliente.
    Guarda el mensaje y devuelve confirmación con timestamp ISO.
    """
    with closing(conn):
        ip_cliente = addr[0]
        # Recibir un mensaje
        texto = recibir_texto(conn)
        if not texto:
            # Cliente cerró sin enviar datos
            return

        # Timestamp en formato ISO 8601 con zona horaria UTC (o local si preferís)
        ahora = datetime.datetime.now().isoformat(timespec="seconds")

        # Guardar en DB
        guardar_mensaje(db_conn, texto, ahora, ip_cliente)
        print(f"[MSG] {ip_cliente} @ {ahora}: {texto}")

        # Responder al cliente
        responder(conn, f"Mensaje recibido: {ahora}")

def servir_por_siempre(srv_sock: socket.socket, db_conn: sqlite3.Connection) -> None:
    """
    Bucle principal del servidor: aceptar conexiones y atender clientes.
    """
    try:
        while True:
            conn, addr = srv_sock.accept()  # Aceptar una nueva conexión
            atender_cliente(conn, addr, db_conn)
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido por el usuario (Ctrl+C).")
    finally:
        srv_sock.close()
        db_conn.close()
        print("[INFO] Recursos liberados.")

def main():
    # 1) Inicializar DB
    db_conn = init_db(DB_PATH)
    # 2) Inicializar socket
    srv_sock = inicializar_socket(HOST, PORT)
    # 3) Aceptar/atender conexiones
    servir_por_siempre(srv_sock, db_conn)

if __name__ == "__main__":
    main()
