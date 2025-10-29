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
- Más detalles del flujo agentico: ver [AGENTIC_PIPELINE.md](./AGENTIC_PIPELINE.md)

La carpeta `frontend/` contiene una SPA (Vite + React + Tailwind) para interactuar con el pipeline agentico del backend.

Características:

- Carga múltiples archivos (`.txt`, `.pdf`, `.docx`).
- Validación de extensiones soportadas.
- Campo de cliente y flag opcional de enriquecimiento (`enrich_allowed`).
- Llamada al endpoint `POST /context/analyze` usando `multipart/form-data`.
- Render estructurado del resultado (campos nuevos: `industry`, `location`, `engagement_age`, etc.).
- Vista expandible con el JSON completo.

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

- El backend ahora usa agentes (Ingestor → Extractor → Validator → Researcher opcional) con OpenAI GPT-4o.
- Si se marca "Permitir enriquecimiento" se ejecuta el ResearcherAgent y puede demorar más.
- La respuesta mínima incluye `analysis_id`, `status` y `summary` (ClientContext).
- Se ignoran archivos duplicados por nombre en la sesión de carga.
- Posibles mejoras futuras: barra de progreso, drag & drop, límites de tamaño, internacionalización, theming, pooling de estados si se hace async largo.

## CI

Se incluye workflow de GitHub Actions para correr tests en cada push/PR.

## Licencia

MIT (ver archivo `LICENSE`).

## Contribuciones

Pull requests bienvenidas mientras el alcance siga el roadmap minimal.

---

> MVP orientado a acelerar discovery inicial antes de la integración de modelos generativos.

---

## 🚀 Integración AutoGen (Pipeline de Agentes)

Se ha incorporado una arquitectura basada en agentes usando la librería **AutoGen (agentchat + core + ext[openai])** con el modelo `gpt-4o` para transformar materiales de entrada (RFPs, briefs, URLs) en un JSON estructurado listo para ser consumido por otros sistemas o agentes.

### Agentes

| Agente | Responsabilidad | Input | Output |
|--------|-----------------|-------|--------|
| Ingestor | Lee archivos (PDF, DOCX, TXT) o URLs y normaliza el texto, agregando metadatos (páginas, anchors). | Ruta de archivo / URL | `{ text_blocks: [...], metadata: {...} }` |
| Extractor | Convierte bloques de texto + metadatos en el esquema de negocio (`ClientContext`), con evidencias (anchors). | `text_blocks`, `metadata` | JSON parcial con campos + `evidence` |
| Validator | Valida contra el modelo Pydantic (`ClientContext`), intenta reparar campos faltantes. | JSON extraído | JSON validado / reparado |
| Researcher (opcional) | Enriquece campos faltantes usando información pública (si está permitido). | JSON validado | JSON enriquecido + `sources` |
| Coordinator | Orquesta el flujo completo y devuelve el resultado final + log. | Parámetros de request | `{ final_json, log }` |

### Flujo

1. El endpoint `/context/analyze` recibe archivos o texto plano.
2. `CoordinatorAgent.run_pipeline()` ejecuta secuencialmente:
   - `IngestorAgent.ingest()` → extracción y normalización.
   - `ExtractorAgent.extract()` (async) → generación estructurada usando LLM.
   - `ValidatorAgent.validate()` (async) → verificación / reparación.
   - `ResearcherAgent.enrich()` (async, condicional) → enriquecimiento externo.
3. Se construye un `AnalyzeResponse` con los campos del modelo `ClientContext`.

### Async / LLM

- Los métodos de extracción, validación y enriquecimiento son `async` y usan `await agent.run(task=...)` para interactuar con el modelo.
- La respuesta del LLM se parsea en JSON directo; si el modelo incluye texto adicional, se aplica un fallback regex controlado.

### Archivos Clave

```text
app/services/agentic/
  ingestor_agent.py       # Lectura de PDF/DOCX/TXT/URL y normalización
  extractor_agent.py      # LLM → JSON estructurado + evidencias
  validator_agent.py      # Validación Pydantic + reparación asistida por LLM
  researcher_agent.py     # Enriquecimiento público opcional
  coordinator_agent.py    # Orquestación del pipeline async
```

### Ejemplo Simplificado de Uso Interno

```python
from app.services.agentic.coordinator_agent import CoordinatorAgent

coordinator = CoordinatorAgent()
result = await coordinator.run_pipeline(file_path="./samples/brief.txt", enrich_allowed=False)
print(result["final_json"])
```

### Variables de Entorno

Asegúrate de definir `OPENAI_API_KEY` en `.env` y cargarlo temprano en `app/main.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Manejo de Errores

- Si el LLM no produce JSON válido: se retorna `{ "error": ..., "raw_response": ... }` en la etapa correspondiente.
- Validaciones fallidas: el `ValidatorAgent` intenta reparación; si no es posible, conserva campos vacíos.
- Enriquecimiento deshabilitado: `ResearcherAgent` devuelve `{ "error": "Enrichment not allowed." }` y el pipeline continúa.


### Estado Actual

- Pipeline funcional MVP.
- Falta: tests específicos para cada agente y mocks de LLM. Eliminar metodos deprecados

---
