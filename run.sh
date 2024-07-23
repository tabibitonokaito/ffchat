#!/bin/bash

# Obtener la ruta del directorio donde está el script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activar el entorno virtual
source "$SCRIPT_DIR/venv/bin/activate"

# Establecer PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR"

# Ejecutar el script Python
python "$SCRIPT_DIR/main.py"
