#!/usr/bin/env python3
"""
Auto-MD: Corrector automático de archivos Markdown usando LLM local.
"""

import argparse
import os
import sys
import time
import requests
import yaml
from pathlib import Path
from difflib import unified_diff, ndiff
from colorama import init, Fore, Back, Style

def load_config():
    """Carga la configuración desde config.yaml."""
    config_path = Path(__file__).parent / 'config.yaml'
    # Si hay configuración cargada:
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    # Si no hay configuración, valores por defecto:
    return {
        'ollama_host': 'http://localhost:11434',
        'model': 'qwen2.5:7b',
        'timeout': 60
    }

def get_files_to_process(path, days=None):
    """Obtiene la lista de archivos .md a procesar."""
    path = Path(path)
    if path.is_file():
        if path.suffix == '.md':
            return [path]
        else:
            print(f"Error: {path} no es un archivo .md")
            return []
    elif path.is_dir():
        files = list(path.rglob('*.md'))
        if days:
            cutoff = time.time() - (days * 24 * 60 * 60)
            files = [f for f in files if f.stat().st_mtime > cutoff]
        return files
    else:
        print(f"Error: {path} no existe")
        return []

def correct_text(text, config):
    """Corrige el texto usando el LLM."""
    system_prompt = """Sos un corrector ortográfico de notas escritas en español. Tu única tarea es corregir errores de ortografía y formato Markdown. Devolvés ÚNICAMENTE el texto corregido, sin comentarios, sin traducciones, sin explicaciones."""

    prompt = f"""Corregí los errores ortográficos y de formato Markdown del siguiente texto.

IMPORTANTE:
- NUNCA DEBES HACER TRADUCCIONES
- La ortografía debe ser perfecta
- Las palabras y términos en inglés que aparezcan (términos técnicos, nombres propios, etc.) déjalas exactamente como están, solo corregí si tienen un error tipográfico evidente (ej: "lerning" → "learning")
- No toques bloques de código (entre ` o ```)
- Hacé modificaciones de la estructura Markdown para que el texto sea más fácil de leer, pero SIN AFECTAR EL SIGNIFICADO. Por ejemplo, agregar encabezados si la estructura del texto lo evidencia
- No reescribas frases ni cambies el significado
- Respondé SOLO con el texto corregido, nada más

TEXTO:
{text}"""

    try:
        response = requests.post(
            f"{config['ollama_host']}/api/generate",
            json={
                "model": config['model'],
                "system": system_prompt,
                "prompt": prompt,
                "stream": False
            },
            timeout=config['timeout']
        )
        response.raise_for_status()
        result = response.json()
        return result['response'].strip()
    except Exception as e:
        print(f"Error al corregir texto: {e}")
        return text

def show_colored_diff(original, corrected, file_path):
    """Muestra diferencias coloreadas línea por línea."""
    init(autoreset=True)
    print(f"Diferencias para {file_path}:")
    diff = ndiff(original.splitlines(), corrected.splitlines())
    for line in diff:
        if line.startswith('+ '):
            print(Fore.GREEN + line)
        elif line.startswith('- '):
            print(Fore.RED + line)
        elif line.startswith('? '):
            print(Fore.YELLOW + line)
        else:
            print(line)

def process_file(file_path, config, dry_run=False, show_diff_flag=False):
    """Procesa un archivo individual."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
        return

    corrected = correct_text(original, config)

    if original == corrected:
        print(f"No hay cambios en {file_path}")
        return

    # Si se pidió preview (diff o dry-run), mostrar y preguntar confirmación
    if show_diff_flag or dry_run:
        if show_diff_flag:
            show_colored_diff(original, corrected, file_path)
        if dry_run:
            print(f"Archivo corregido completo para {file_path}:")
            print(corrected)
        
        response = input(f"¿Aplicar cambios a {file_path}? (s/n): ").strip().lower()
        if response != 's':
            print(f"Cambios rechazados para {file_path}")
            return

    # Si llega aquí, aplicar cambios (confirmado o sin flags)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(corrected)
        print(f"Corregido: {file_path}")
    except Exception as e:
        print(f"Error al escribir {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Corrector automático de Markdown")
    parser.add_argument('path', help='Ruta al archivo .md o carpeta')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar cambios y preguntar confirmación antes de aplicar')
    parser.add_argument('--diff', action='store_true', help='Mostrar diff y preguntar confirmación antes de aplicar')
    parser.add_argument('--days', type=int, help='Solo archivos modificados en los últimos N días')

    args = parser.parse_args()

    config = load_config()
    files = get_files_to_process(args.path, args.days)

    if not files:
        print("No se encontraron archivos para procesar")
        return

    for file_path in files:
        process_file(file_path, config, args.dry_run, args.diff)

if __name__ == '__main__':
    main()