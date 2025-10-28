
import os
import json
import re
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class ExtractorAgent:
    def __init__(self, name="extractor", api_key: str = None, system_message: str = None):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")

        if system_message is None:
            system_message = (
                "You are the Extractor agent. Your job is to convert normalized text blocks and metadata into a strict JSON structure as defined by the application's business context schema. "
                "For each field, extract the relevant information from the text, and provide evidence pointers (such as page numbers, section headers, or text anchors) for each extracted value. "
                "If information is missing or ambiguous, leave the field empty and note the reason in a 'notes' section. Do not hallucinate or invent data. "
                "Output must be a valid JSON object matching the schema provided."
            )

        self.model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
        self.agent = AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    async def extract(self, text_blocks, metadata, schema=None):
        """
        Extracts structured JSON from text_blocks and metadata using GPT-4o, matching the ClientContext schema.
        Args:
            text_blocks (list): List of dicts with 'text' and 'anchor'.
            metadata (dict): Metadata from the ingestor.
            schema (str|None): Optional JSON schema string. If None, uses default ClientContext schema.
        Returns:
            dict: Extracted JSON with evidence pointers.
        """
        if schema is None:
            schema = '''{
                "client_name": "string | null",
                "industry": "string | null",
                "location": "string | null",
                "engagement_age": "int",
                "business_overview": "string | null",
                "objectives": ["string"],
                "company_info": "string | null",
                "additional_context_questions": ["string"],
                "potential_future_opportunities": ["string"]
            }'''

        prompt = (
            "You are an expert information extractor. Given the following text blocks and metadata, extract the required fields for the business context JSON schema. "
            "For each field, provide the value and an evidence pointer (anchor) from the text_blocks. "
            "If a field is missing or ambiguous, leave it null or empty and add a note. Do not invent data.\n"
            f"Schema: {schema}\n"
            f"Metadata: {metadata}\n"
            f"Text blocks: {text_blocks}\n"
            "Return a JSON object matching the schema, and for each field, include an 'evidence' key with the anchor or note."
        )

        # ✅ Run the agent (async) and get the final message
        result = await self.agent.run(task=prompt)
        content = result.messages[-1].content  # final reply content

        try:
            return json.loads(content)
        except Exception as e:
            m = re.search(r'\{[\s\S]*\}', content)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass
            return {"error": f"Failed to parse JSON: {e}", "raw_response": content}
