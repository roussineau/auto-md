# Auto-MD
Auto-MD es un corrector automático de archivos Markdown que usa un LLM local (Ollama + qwen2.5:7b) para mejorar ortografía, estilo y formato sin tocar bloques de código ni cambiar el contenido principal.

## El problema
Al usar Obsidian o cualquier editor Markdown para tomar notas rápidas, es normal cometer errores de tipo ortográfico, de formato o de consistencia (espacios, listas, encabezados).

## La solución
Esta herramienta hace la limpieza de forma automática para que te concentres en el contenido:
- Corrige errores ortográficos en español
- Arregla errores semánticos y palabras mal escritas
- Normaliza Markdown: encabezados, listas, saltos de línea, links, espacios
- Preserva términos técnicos, nombres propios, código y el significado general
- No altera bloques de código (```) ni texto dentro de backticks (`)

## Estructura del repositorio
- `auto-md.py`: script Python principal
- `config.yaml`: configuración de Ollama y modelo
- `requirements.txt`: dependencias Python
- `venv/`: entorno virtual
- `.gitignore`: ignora `venv/`

## Requisitos previos
- Python 3.10+ instalado
- Ollama instalado en la máquina que ejecuta el script
- Modelo `qwen2.5:7b` descargado en Ollama

## Instalar y preparar
```bash
cd ~/auto-md
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:7b
ollama serve
```

## Uso básico
### 1. Corregir todo el vault modificado en los últimos 7 días
```bash
python auto-md.py ~/vault --days 7
```

### 2. Ver propuesta sin modificar archivos
```bash
python auto-md.py ~/vault/apuntes --dry-run
```

### 3. Ver diferencias antes de aplicar
```bash
python auto-md.py ~/vault --diff
```

### 4. Corregir un archivo específico
```bash
python auto-md.py ~/vault/apuntes/clase-hoy.md
```

## Opciones del script
- `path`: ruta a archivo `.md` o carpeta
- `--dry-run`: no escribe cambios, solo muestra salida
- `--diff`: muestra `unified_diff` de antes/después
- `--days N`: procesa solo archivos modificados en los últimos N días

## Cómo funciona internamente
1. `load_config()` lee `config.yaml` (o valores por defecto).
2. `get_files_to_process(path, days)` selecciona archivos `.md` válidos.
3. Por cada archivo:
   - `process_file()` lee contenido
   - `correct_text()` envía el prompt a Ollama
   - Si hay cambios, `--dry-run` muestra, si no escribe en disco
   - `--diff` muestra diff para revisión

## Estado esperado de la configuración
- Ollama levantado en `localhost:11434`
- Modelo `qwen2.5:7b` descargado y disponible
- Entorno virtual activo y dependencias instaladas

## Personalización
- Se puede modificar el prompt de la función `correct_text` para que trabaje en otro idioma.
- Se puede cambiar de modelo por uno más ligero o pesado, conociendo las implicaciones que esto tendría en la salida.

---

`Auto-MD` está diseñado para ser un ayudante ligero: no busca reescribir tus ideas, solo pulir el formato y errores obvios.
