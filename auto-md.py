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
from difflib import unified_diff

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
    prompt = f"""Eres un corrector de Markdown especializado en español. Tu tarea es corregir errores ortográficos, semánticos obvios y limpiar el formato Markdown, pero manteniendo intacto el contenido original.

INSTRUCCIONES ESPECÍFICAS:
✅ Corregir errores ortográficos en español y en inglés.
✅ Corregir errores semánticos obvios (como palabras mal escritas o frases incoherentes)
✅ Limpiar Markdown: encabezados, listas, espacios, links
✅ Cuando lo amerite, agregar encabezados u otras estructuras Markdown que faciliten la lectura comprensiva
❌ NO hacer traducciones
❌ NO cambiar términos técnicos, nombres propios, código
❌ NO alterar el significado ni reescribir frases
❌ NO tocar bloques de código (entre backticks ``` o `)
❌ Devolver SOLO el texto corregido, sin comentarios ni explicaciones

Texto a corregir:
{text}

Texto corregido:"""

    try:
        response = requests.post(
            f"{config['ollama_host']}/api/generate",
            json={
                "model": config['model'],
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

def show_diff(original, corrected, file_path):
    """Muestra el diff entre original y corregido."""
    diff = unified_diff(
        original.splitlines(keepends=True),
        corrected.splitlines(keepends=True),
        fromfile=str(file_path),
        tofile=str(file_path) + " (corregido)"
    )
    print("".join(diff))

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

    if show_diff_flag:
        show_diff(original, corrected, file_path)

    if dry_run:
        print(f"Cambios propuestos para {file_path}:")
        print(corrected[:500] + "..." if len(corrected) > 500 else corrected)
    else:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(corrected)
            print(f"Corregido: {file_path}")
        except Exception as e:
            print(f"Error al escribir {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Corrector automático de Markdown")
    parser.add_argument('path', help='Ruta al archivo .md o carpeta')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar cambios sin escribir')
    parser.add_argument('--diff', action='store_true', help='Mostrar diff antes de confirmar')
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