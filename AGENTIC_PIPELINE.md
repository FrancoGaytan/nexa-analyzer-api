# Pipeline Agentico de Nexa Analyzer

Este documento resume, paso a paso y de forma simple, cómo el conjunto de agentes (Coordinator + Ingestor + Extractor + Validator + Researcher opcional) transforma un documento o bloque de texto en el `AnalyzeResponse` final consumido por el frontend.

## Visión General

Entrada posible:

- Archivo (`.pdf`, `.docx`, `.txt`) – por ahora se procesa el primero.
- Texto plano (string con varios bloques).

Salida:

- JSON estructurado (`ClientContext`) envuelto en `AnalyzeResponse` con `status` y `analysis_id`.

## Flujo de Pasamanos

1. CoordinatorAgent (orquestador)
   - Punto de entrada del endpoint `/context/analyze` cuando existe `OPENAI_API_KEY`.
   - Decide la secuencia: Ingestor → Extractor → Validator → (Researcher si `enrich_allowed`).
   - Registra un `log` (lista de pasos y resultados intermedios). El API hoy sólo expone el JSON final, pero internamente se conserva ese log para extensión futura.

2. IngestorAgent (normalización de fuente)
   - Detecta tipo de fuente (pdf / docx / txt / url).
   - Extrae contenido en una lista de `text_blocks`: cada elemento incluye `text` + `anchor` (referencia: página, párrafo, línea, bloque).
   - Genera metadatos: páginas, párrafos, líneas, url, etc.
   - Entrega: `{ 'text_blocks': [...], 'metadata': {...} }`.

3. ExtractorAgent (estructuración semántica)
   - Recibe `text_blocks` y `metadata` crudos.
   - Construye un prompt con el esquema destino (campos de `ClientContext`).
   - Llama al modelo (GPT-4o) para producir un JSON que:
     - Rellena campos (industry, location, objectives, etc.).
     - Idealmente incluye evidencias (anchors) o notas si faltan datos.
   - Intento de parseo robusto: si falla parseo directo, busca primer bloque `{ ... }`.
   - Entrega: `dict` de datos candidatos (puede tener errores de formato).

4. ValidatorAgent (sanitización y reparación)
   - Intenta instanciar el Pydantic `ClientContext` con el JSON.
   - Si valida: retorna `validated.dict()`. Si falla:
     - Prompt a GPT para “reparar” el JSON según el schema.
     - Reintenta parsear respuesta.
   - Entrega: JSON conforme al schema (o JSON con campo `error`).

5. ResearcherAgent (enriquecimiento opcional)
   - Sólo si `enrich_allowed = True`.
   - Revisa campos vacíos/ambiguos y busca enriquecer con información pública.
   - Agrega referencias (sources) para cada campo enriquecido.
   - Entrega: JSON enriquecido (o mensaje de error si no procede).

6. CoordinatorAgent (finalización)
   - Selecciona el JSON final (enriquecido o validado).
   - Combina en estructura `{"final_json": <JSON>, "log": [...] }`.
   - El endpoint convierte eso en `AnalyzeResponse`:
     - `analysis_id`: ahora un literal (puede evolucionar a UUID o hash de pipeline).
     - `status`: "completed" si hay `final_json`, "error" en caso contrario.
     - `summary`: los campos de `ClientContext`.

## Tabla Resumen de Inputs / Outputs por Agente

| Agente | Input Principal | Output Principal | Propósito | Posibles Errores | Recuperación |
|--------|-----------------|------------------|-----------|------------------|--------------|
| Ingestor | `file_path` o `url` | `{ text_blocks: [{text, anchor}], metadata: {...} }` | Normalizar y segmentar fuente | Tipo de archivo no soportado | Lanzar `ValueError`; endpoint podría informar al cliente |
| Extractor | `text_blocks`, `metadata` | `raw_json` (estructura cercana a schema) | Extraer campos semánticos iniciales | JSON malformado / no parseable | Regex fallback buscando primer `{ ... }` |
| Validator | `raw_json` | `validated_json` (conforme a `ClientContext`) | Reparar y garantizar formato final | Fallo al validar/reparar | Devuelve JSON con `error` y contenido bruto |
| Researcher (opcional) | `validated_json` + flag `allowed` | `enriched_json` (campos completados + sources) | Completar vacíos con info pública | Sin fuentes fiables / tiempo excedido | Devolver sin cambios o mensaje `error` |
| Coordinator | Resultados parciales de cada agente | `{ final_json, log }` | Orquestar secuencia y consolidar | Error en agente individual | Puede abortar con estado `error` y log parcial |


## Diagrama Secuencial Simplificado

```text
[Request] --> Coordinator
Coordinator -> Ingestor: ingest(file|text)
Ingestor --> Coordinator: {text_blocks, metadata}
Coordinator -> Extractor: extract(text_blocks, metadata)
Extractor --> Coordinator: raw_json
Coordinator -> Validator: validate(raw_json)
Validator --> Coordinator: validated_json
Coordinator -> Researcher (opcional): enrich(validated_json)
Researcher --> Coordinator: enriched_json
Coordinator: decide final_json
Coordinator --> API Response Transformer: AnalyzeResponse
```

## Manejo de Errores (High Level)

- Falta `OPENAI_API_KEY`: el endpoint (si se reintroduce fallback) puede regresar heurísticas o error explícito.
- Parseo fallido en Extractor: intenta regex para primer `{}`.
- Validación fallida en Validator: repara vía modelo; si vuelve a fallar, se coloca un JSON con `error`.
- Enriquecimiento no permitido: devuelve JSON original sin cambios.

## Campos Principales del ClientContext

- `client_name`: nombre del cliente si se detecta.
- `industry`, `location`, `engagement_age`: metadata contextual.
- `business_overview`: resumen general extraído.
- `objectives`: lista de objetivos detectados.
- `company_info`: descripción adicional.
- `additional_context_questions`: pistas o gaps para profundizar.
- `potential_future_opportunities`: ideas de evolución futura.

## Extensiones Futuras

- Exponer el `log` completo vía endpoint `/context/analyze?include_log=true`.
- Añadir un ID único (UUID) generado por pipeline.
- Soporte multi-archivo simultáneo (merging inteligente de anchors).
- Evidencias explícitas: `field_evidence: { field: [anchors] }`.
- Persistencia de resultados y auditoría.

## Uso Rápido (Dev)

1. Definir `OPENAI_API_KEY` en `.env`.
2. (Opcional) `CORS_ORIGINS=http://localhost:5173` para frontend.
3. Levantar backend: `uvicorn app.main:app --reload`.
4. Frontend hace `POST /context/analyze` con form-data `files` o `raw_text_blocks` + `enrich_allowed`.
5. Recibes `AnalyzeResponse.summary` con el contexto.

---
Este pipeline modular permite reemplazar o mejorar cada etapa sin afectar las demás (por ejemplo: nuevo Extractor con embeddings, Validator con reglas adicionales, Researcher con herramientas web).
