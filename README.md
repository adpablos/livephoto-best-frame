# Video Frame Extractor

Este script de Python está diseñado para extraer automáticamente el frame más nítido de cada video MP4 en un directorio específico. Utiliza técnicas de procesamiento de imagen para evaluar la nitidez de cada frame y seleccionar el mejor.

## 🎯 Problema que resuelve

Frecuentemente necesitamos obtener una imagen representativa y de alta calidad de un video. En lugar de extraer un frame aleatorio o el primer frame (que podría estar borroso o ser de baja calidad), este script:

- Analiza todos los frames del video
- Evalúa la nitidez de cada frame usando el operador Laplaciano
- Selecciona y guarda el frame más nítido
- Procesa múltiples videos en lote

## 🚀 Características

- Procesamiento por lotes de videos MP4
- Detección automática del frame más nítido
- Soporte para formatos de salida JPG y PNG
- Sistema de logging detallado
- Manejo robusto de errores
- Interfaz por línea de comandos

## 📋 Requisitos

```bash
pip install opencv- 