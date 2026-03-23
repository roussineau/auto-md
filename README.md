# Auto-MD
Auto-MD es un corrector automático de archivos Markdown que usa un LLM local para mejorar ortografía, estilo y formato sin tocar bloques de código ni cambiar el contenido principal.

## El problema
Al usar Obsidian o cualquier editor Markdown para tomar notas rápidas, es normal cometer errores de tipo ortográfico, de formato o de consistencia (espacios, listas, encabezados).

## La solución
Esta herramienta hace la limpieza de forma automática para que te concentres en el contenido:
- Corrige errores ortográficos
- Arregla errores semánticos y palabras mal escritas
- Normaliza y mejora Markdown: encabezados, listas, saltos de línea, links, espacios
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
- Modelo `qwen2.5:7b` descargado en Ollama, aunque puede ser reemplazado por otro elegido por el usuario

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

### 2. Ver propuesta antes de confirmar cambios
```bash
python auto-md.py ~/vault/apuntes --dry-run
```

### 3. Ver diferencias antes de confirmar cambios
```bash
python auto-md.py ~/vault --diff
```

### 4. Corregir un archivo específico
```bash
python auto-md.py ~/vault/apuntes/clase-hoy.md
```

## Opciones del script
- `path`: ruta a archivo `.md` o carpeta
- `--dry-run`: muestra el archivo completo corregido y pregunta confirmación antes de aplicar
- `--diff`: muestra diferencias coloreadas y pregunta confirmación antes de aplicar
- `--days N`: procesa solo archivos modificados en los últimos N días

## Cómo funciona internamente
1. `load_config()` lee `config.yaml` (o valores por defecto).
2. `get_files_to_process(path, days)` selecciona archivos `.md` válidos.
3. Por cada archivo:
   - `process_file()` lee contenido
   - `correct_text()` envía el prompt a Ollama
   - Si `--dry-run` o `--diff`, muestra cambios/diff y pregunta confirmación
   - Solo escribe en disco si el usuario confirma (o si no hay flags)

## Estado esperado de la configuración
- Ollama levantado en `localhost:11434`
- Modelo `qwen2.5:7b` descargado y disponible
- Entorno virtual activo y dependencias instaladas

## Personalización
- Se puede modificar el prompt de la función `correct_text`.
- Se puede cambiar de modelo por uno más ligero o pesado, considerando las implicaciones que esto tendría en la salida.

---

`Auto-MD` está diseñado para ser un ayudante ligero: no busca reescribir tus ideas, solo pulir el formato y errores obvios.
