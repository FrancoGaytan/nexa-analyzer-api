import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .ingestor_agent import IngestorAgent
from .extractor_agent import ExtractorAgent
from .validator_agent import ValidatorAgent
from .researcher_agent import ResearcherAgent

class CoordinatorAgent:
    def __init__(self, name="coordinator", api_key: str = None, system_message: str = None):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")

        if system_message is None:
            system_message = (
                "You are the Coordinator agent. Your job is to orchestrate the Ingestor, Extractor, Validator, and Researcher agents to process client-provided materials and produce a final, validated business context JSON. "
                "You must manage the workflow: Ingestor → Extractor → Validator → (Researcher, if allowed), and ensure the output is complete, accurate, and ready for downstream consumption. "
                "Return the final JSON object and a log of the workflow steps."
            )

        self.model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
        self.agent = AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    async def run_pipeline(self, file_path: str = None, file_paths: list = None, url: str = None, enrich_allowed: bool = False):
        """
        Orchestrates the workflow: Ingestor → Extractor → Validator → (Researcher, if allowed).
        Args:
            file_path (str): Path to the input file (PDF, DOCX, TXT).
            url (str): URL to ingest.
            enrich_allowed (bool): Whether to allow enrichment with public info.
        Returns:
            dict: { 'final_json': ..., 'log': [...] }
        """
        log = []

        ingestor = IngestorAgent()
        extractor = ExtractorAgent()
        validator = ValidatorAgent()
        researcher = ResearcherAgent()

        # Step 1: Ingest
        log.append("Ingesting input...")
        if file_paths:
            # Ingest all files and merge their text_blocks and metadata
            all_blocks = []
            all_metadata = {"files": []}
            for fp in file_paths:
                result = ingestor.ingest(file_path=fp)
                all_blocks.extend(result["text_blocks"])
                all_metadata["files"].append(result["metadata"])
            ingest_result = {"text_blocks": all_blocks, "metadata": all_metadata}
        else:
            ingest_result = ingestor.ingest(file_path=file_path, url=url)
        log.append({"ingest_result": ingest_result["metadata"]})

        # Step 2: Extract (async)
        log.append("Extracting structured JSON...")
        extract_result = await extractor.extract(ingest_result["text_blocks"], ingest_result["metadata"])
        log.append({"extract_result": extract_result})

        # Step 3: Validate (async)
        log.append("Validating and repairing JSON...")
        validate_result = await validator.validate(extract_result)
        log.append({"validate_result": validate_result})

        # Step 4: Research (optional, async)
        if enrich_allowed:
            log.append("Enriching missing/ambiguous fields with public info...")
            enrich_result = await researcher.enrich(validate_result, allowed=True)
            log.append({"enrich_result": enrich_result})
            final_json = enrich_result
        else:
            final_json = validate_result

        log.append("Pipeline complete.")
        return {"final_json": final_json, "log": log}
