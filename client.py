#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente de chat básico.
- Se conecta a localhost:5000
- Permite enviar múltiples mensajes hasta que el usuario escriba "éxito"
- Muestra la respuesta del servidor para cada mensaje
"""

import socket
import sys

HOST = "127.0.0.1"
PORT = 5000

def conectar(host: str, port: int) -> socket.socket:
    """
    Crea un socket y se conecta al servidor.
    Maneja errores de conexión (servidor no disponible).
    """
    try:
        cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli_sock.connect((host, port))
        return cli_sock
    except OSError as e:
        print(f"[ERROR] No se pudo conectar con {host}:{port}: {e}", file=sys.stderr)
        sys.exit(3)

def enviar_recibir(cli_sock: socket.socket, texto: str) -> str:
    """
    Envía un texto al servidor y espera respuesta.
    """
    cli_sock.sendall(texto.encode('utf-8'))
    data = cli_sock.recv(4096)
    if not data:
        return "[WARN] El servidor cerró la conexión sin respuesta."
    return data.decode('utf-8', errors='replace')

def main():
    print("Cliente de chat. Escribí tus mensajes y presioná Enter.")
    print("Para terminar, escribí: éxito")
    while True:
        try:
            texto = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Finalizando cliente.")
            break

        if texto.lower() in ("éxito", "exito"):
            print("[INFO] ¡Gracias! Saliendo...")
            break

        # Se abre una conexión por mensaje para simplificar el protocolo
        sock = conectar(HOST, PORT)
        respuesta = enviar_recibir(sock, texto)
        print(f"[SERVIDOR] {respuesta}")
        sock.close()

if __name__ == "__main__":
    main()
