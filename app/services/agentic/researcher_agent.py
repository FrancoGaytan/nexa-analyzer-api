
import os
import json
import re
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class ResearcherAgent:
    def __init__(self, name="researcher", api_key: str = None, system_message="Enriches missing/ambiguous fields using public info."):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")
        self.model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
        self.agent = AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    async def enrich(self, data: dict, allowed: bool = True):
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
            "Industry refers to the primary sector in which the client operates (e.g., Healthcare, Finance, Technology).\n"
            "Location refers to the primary geographic location of the client (e.g., city, country).\n"
            "Business Overview is a brief summary of the client's business operations and goals. Try to be complete and thorough.\n"
            "Objectives are the main goals the client aims to achieve through their partnership with Endava. Try to be complete, specific and detailed.\n"
            "Company Info includes relevant details about the client's size, market position, and key offerings. Try to be complete and thorough.\n"
            "Additional Context Questions are any questions that arise from the provided materials that need clarification from the client.\n"
            "Potential Future Opportunities are possible areas for growth or collaboration that could be explored in the future.\n"
            "Return only the enriched JSON object, with a 'sources' key for each enriched field."
        )
        result = await self.agent.run(task=prompt)
        content = result.messages[-1].content
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
