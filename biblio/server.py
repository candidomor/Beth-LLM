#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Local de Artigos - Projeto Beth LLM
Mestrado em Computação Aplicada | Modelos Generativos de Linguagem
"""

import http.server
import socketserver
import os
import sys
import json
import webbrowser
import threading
import time

# Ensure UTF-8 output in Windows terminal
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class AcademicBiblioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # API endpoint for papers JSON
        if self.path == '/api/papers' or self.path == '/api/papers/':
            json_path = os.path.join(DIRECTORY, 'papers_data.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(data.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
                return
            else:
                self.send_error(404, "Arquivo papers_data.json nao encontrado.")
                return

        # Handle PDF files with proper inline headers
        if self.path.startswith('/papers/'):
            filename = self.path[len('/papers/'):].split('?')[0]
            file_path = os.path.join(DIRECTORY, 'papers', filename)
            if os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'inline; filename="{os.path.basename(file_path)}"')
                self.send_header('Content-Length', str(os.path.getsize(file_path)))
                self.end_headers()
                with open(file_path, 'rb') as f:
                    while chunk := f.read(64 * 1024):
                        self.wfile.write(chunk)
                return

        # Fallback to standard handler
        return super().do_GET()

def run_server(start_port=8000, auto_open=True):
    socketserver.TCPServer.allow_reuse_address = True
    handler = AcademicBiblioHandler

    # Load stats
    json_path = os.path.join(DIRECTORY, 'papers_data.json')
    total_papers = 33
    downloaded = 15
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_papers = len(data)
                downloaded = sum(1 for p in data if p.get('download_status') == 'Downloaded')
        except Exception:
            pass

    httpd = None
    port = start_port
    max_port = start_port + 50
    while port < max_port:
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            port += 1

    if not httpd:
        print(f"Erro: Nenhuma porta disponivel entre {start_port} e {max_port}.")
        return

    server_url = f"http://localhost:{port}"

    print("=" * 70)
    print(" [SERVICO] Biblioteca de Artigos - Beth LLM")
    print(" Disciplina: Modelos Generativos de Linguagem (Mestrado Computacao)")
    print("=" * 70)
    print(f" -> Total catalogado:    {total_papers} artigos")
    print(f" -> PDFs locais prontos: {downloaded} artigos disponiveis offline")
    print(f" -> Links externos:      {total_papers - downloaded} artigos/datasets oficiais")
    print("-" * 70)
    print(f" Servidor disponivel em: {server_url}")
    print(f" Diretorio dos PDFs:    {os.path.join(DIRECTORY, 'papers')}")
    print(" Pressione Ctrl+C para encerrar o servidor.")
    print("=" * 70)

    if auto_open:
        def open_browser():
            time.sleep(0.8)
            webbrowser.open(server_url)
        threading.Thread(target=open_browser, daemon=True).start()

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrando o servidor da biblioteca. Ate logo!")
            httpd.shutdown()

if __name__ == '__main__':
    auto_open = '--no-browser' not in sys.argv
    start_port = 8000
    for arg in sys.argv[1:]:
        if arg.isdigit():
            start_port = int(arg)
            break
    run_server(start_port=start_port, auto_open=auto_open)
