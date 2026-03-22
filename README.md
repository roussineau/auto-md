# Auto-MD
Usa un LLM local para corregir archivos Markdown.

## El problema
Si usas Obsidian para tomar notas en tiempo real, sabes que corregir errores ortográficos y de formato después es una tarea repetitiva.

## La solución
Auto-MD usa un LLM local y un script en Python para automatizar esas correcciones, manteniendo la privacidad al no salir de tu máquina.

## Instalación
1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Asegurarse de que Ollama esté corriendo con el modelo que queremos. En este caso, el default del proyeco es qwen2.5:7b:
   ```bash
   ollama serve
   ollama pull qwen2.5:7b
   ```

3. Configura en `config.yaml` si es necesario (por defecto usa localhost y el modelo mencionado).

## Uso
```bash
# Corregir todas las notas modificadas en los últimos 7 días
python auto-md.py ~/vault --days 7

# Ver qué cambiaría sin modificar nada
python auto-md.py ~/vault/apuntes --dry-run

# Procesar una nota específica
python auto-md.py ~/vault/apuntes/clase-hoy.md

# Mostrar diff antes de confirmar
python auto-md.py ~/vault --diff
```

## Opciones
- `ruta`: Archivo .md o carpeta con archivos .md
- `--dry-run`: Muestra cambios sin escribir
- `--diff`: Muestra un diff antes de confirmar
- `--days N`: Solo archivos modificados en los últimos N días

## Arquitectura
- Ejecuta en máquina con GPU usando Ollama local
- Opción para llamar a Ollama en otra máquina por red (configura `ollama_host` en config.yaml)

## Lo que corrige
✅ Errores ortográficos en español
✅ Errores semánticos obvios
✅ Limpieza de Markdown (encabezados, listas, espacios, links)
❌ No cambia términos técnicos, nombres propios, código
❌ No altera el significado ni reescribe frases
❌ No toca bloques de código