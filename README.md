# Nexa Analyzer API

[![CI](https://github.com/FrancoGaytan/nexa-analyzer-api/actions/workflows/ci.yml/badge.svg)](https://github.com/FrancoGaytan/nexa-analyzer-api/actions/workflows/ci.yml)

API (MVP) para extraer rápidamente contexto estructurado desde texto libre o documentos (RFPs, briefs) y devolver un JSON mínimo con: objetivos, requisitos técnicos, oportunidades futuras y campos básicos de cliente. Implementado con FastAPI + Pydantic v2. Próximo paso: integrar un LLM para enriquecer el análisis.

## Características actuales

- Endpoint único `POST /context/analyze` que acepta:
	- `client_name` (form field obligatorio)
	- `raw_text_blocks` (string JSON opcional: lista de bloques de texto)
	- `files` (0..n archivos: `.txt`, `.pdf`, `.docx`)
- Heurísticas simples (keywords) para detectar objetivos, requisitos técnicos y oportunidades futuras.
- Extracción de texto de PDF (pypdf), DOCX (python-docx) y TXT.
- Respuesta inmediata siempre con `status = "completed"`.
- Tests automatizados (`pytest`).

## Requisitos

- Python 3.13
- uv instalado (<https://docs.astral.sh/uv/>)

## Instalación

```powershell
# Activar entorno (si no se creó, primero: uv venv)
. .\.venv\Scripts\Activate.ps1
uv sync  # instala dependencias declaradas en pyproject.toml
```

## Ejecutar servidor (modo desarrollo)

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Si `uv run` funciona en tu entorno:

```powershell
uv run uvicorn app.main:app --reload --port 8000
```

## Endpoints

### Health

`GET /health` → `{ "status": "ok" }`

### Análisis de contexto

`POST /context/analyze`

Content-Type: `multipart/form-data` o `application/x-www-form-urlencoded` (para solo texto). Campos:

- `client_name`: nombre del cliente (string)
- `raw_text_blocks`: (opcional) JSON serializado de lista de strings
- `files`: (opcional) lista de archivos

Ejemplo de respuesta:

```json
{
  "analysis_id": "<uuid>",
  "status": "completed",
  "client_name": "ACME Logistics",
  "summary": {
    "business_overview": null,
    "objectives": ["Reducir costos", "Integrar sistemas existentes"],
    "company_info": null,
    "technical_requirements": ["Integración con ERP SAP"],
    "project_timeline": null,
    "additional_context_questions": [],
    "potential_future_opportunities": ["Optimización futura con analítica avanzada"]
  }
}
```

## Ejemplos (PowerShell / Windows)

### Solo texto

```powershell
curl.exe -X POST ^
  -F "client_name=ACME Logistics" ^
  -F "raw_text_blocks=[\"Queremos reducir costos y mejorar integración con SAP.\"]" ^
  http://localhost:8000/context/analyze
```

### Con archivo

```powershell
curl.exe -X POST ^
  -F "client_name=ACME Logistics" ^
  -F "files=@samples/brief.txt" ^
  http://localhost:8000/context/analyze
```

## Estructura (parcial)

```text
app/
  main.py
  api/routes/context.py
  api/routes/health.py
  models/context.py
  services/context_analyzer_service.py
tests/
  test_health.py
  test_context.py
samples/
  brief.txt
```

## Tests

```powershell
uv run pytest -q
```

## Roadmap corto

- [ ] Integrar LLM (OpenAI u otro) para enriquecer summary
- [ ] Persistencia (historial de análisis) con una base ligera (SQLite / Postgres)
- [ ] Logging estructurado + correlación de requests
- [ ] Dockerfile + composición para despliegue
- [ ] Campos adicionales (riesgos, KPIs, stakeholders, confidences)
- [ ] Mejora heurísticas (detección timeline, riesgos, métricas)

## Frontend (MVP UI)

Se agregó una carpeta `frontend/` con una Single Page App (Vite + React + Tailwind) mínima para:

- Cargar múltiples archivos (`.txt`, `.pdf`, `.docx`).
- Validar extensiones soportadas (mismas que backend: ver `SUPPORTED_*_EXT`).
- Ingresar el nombre del cliente.
- Enviar el formulario al endpoint `POST /context/analyze` y mostrar el JSON recibido.

### Ejecutar el Frontend

Requisitos: Node 18+ (recomendado), pnpm o npm.

```powershell
cd frontend
# Instalar dependencias
npm install

# Copiar .env.example si se desea cambiar la URL del backend
Copy-Item .env.example .env  # (opcional)

# Ejecutar en modo dev (abre en http://localhost:5173)
npm run dev
```

Si el backend corre en otro puerto/host, ajustar `VITE_API_BASE_URL` en `.env`.

### Build de producción

```powershell
npm run build
npm run preview # (sirve para testear el build)
```

### Notas

- La validación es solo por extensión de archivo (no inspección de contenido) igual que la heurística actual.
- Se ignoran archivos duplicados por nombre en la sesión de carga.
- Posibles mejoras futuras: barra de progreso, drag & drop, tamaño máximo, internacionalización, theming.

## CI

Se incluye workflow de GitHub Actions para correr tests en cada push/PR.

## Licencia

MIT (ver archivo `LICENSE`).

## Contribuciones

Pull requests bienvenidas mientras el alcance siga el roadmap minimal.

---

> MVP orientado a acelerar discovery inicial antes de la integración de modelos generativos.
