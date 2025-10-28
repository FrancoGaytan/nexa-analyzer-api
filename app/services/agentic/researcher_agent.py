
import json
import re
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class ResearcherAgent:
    def __init__(self, name="researcher", system_message="Enriches missing/ambiguous fields using public info."):
        self.model_client = OpenAIChatCompletionClient(model="gpt-4o")
        self.agent = AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    def enrich(self, data: dict, allowed: bool = False):
        """
        Enriches missing/ambiguous fields in the JSON object using public information, only if allowed.
        Args:
            data (dict): The JSON object to enrich.
            allowed (bool): Whether enrichment is permitted.
        Returns:
            dict: Enriched JSON object with source references for each enriched field.
        """
        if not allowed:
            return {"error": "Enrichment not allowed."}

        prompt = (
            "You are a research agent. For the following business context JSON, enrich any missing or ambiguous fields using only publicly available information. "
            "For each field you enrich, provide a source reference (URL or citation). Do not fabricate information. "
            "If you cannot find reliable public information, leave the field empty and add a note explaining why.\n"
            f"JSON: {data}\n"
            "Return only the enriched JSON object, with a 'sources' key for each enriched field."
        )
        response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        try:
            match = re.search(r'{[\s\S]+}', response)
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError("No JSON object found in response.")
        except Exception as e:
            return {"error": str(e), "raw_response": response}
