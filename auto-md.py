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

CHUNK_MAX_WORDS = 600

def split_into_chunks(text, max_words=CHUNK_MAX_WORDS):
    """Divide el texto en chunks por párrafos, sin superar max_words por chunk."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_words = 0

    for paragraph in paragraphs:
        words = len(paragraph.split())
        if current_words + words > max_words and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_words = words
        else:
            current_chunk.append(paragraph)
            current_words += words

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks

def correct_chunk(text, config):
    """Envía un chunk al LLM y devuelve el texto corregido."""
    system_prompt = """You are a spelling corrector for notes written in Spanish. Your only tasks are to fix spelling errors and clean up Markdown formatting. Return ONLY the corrected text, with no comments, no translations, and no explanations."""

    prompt = f"""Fix the spelling errors and Markdown formatting in the following text.

RULES:
- DO NOT translate any word or line.
- Spelling in Spanish MUST be perfect.
- English words (technical terms, proper nouns, etc.) must stay in English exactly as written. Only fix obvious typos in them.
- DO NOT touch code blocks (between ` or ```).
- DO NOT rewrite sentences or change the meaning.
- Markdown fixes must be conservative: fix what is broken, but do not add new structure unless it is very obvious.
- Reply with ONLY the corrected text, nothing else.

TEXT:
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
        return response.json()['response'].strip()
    except Exception as e:
        print(f"Error al corregir chunk: {e}")
        return text

def correct_text(text, config):
    """Corrige el texto completo, dividiéndolo en chunks si es necesario."""
    total_words = len(text.split())

    if total_words <= CHUNK_MAX_WORDS:
        return correct_chunk(text, config)

    chunks = split_into_chunks(text)
    print(f"  Archivo largo ({total_words} palabras), procesando en {len(chunks)} partes...")
    corrected_chunks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  Parte {i}/{len(chunks)}...")
        corrected_chunks.append(correct_chunk(chunk, config))

    return '\n\n'.join(corrected_chunks)

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