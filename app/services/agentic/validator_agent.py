
import re
import os
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class ValidatorAgent:
    def __init__(self, name="validator", api_key: str = None, system_message="Validates and repairs JSON output using schema."):
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
    async def validate(self, data: dict, schema_model=None):
        """
        Validates and repairs a JSON object using a Pydantic model. If repair is needed, uses GPT-4o to suggest fixes.
        Args:
            data (dict): The JSON object to validate.
            schema_model (BaseModel|None): The Pydantic model to validate against. If None, uses ClientContext.
        Returns:
            dict: Validated and (if needed) repaired JSON object.
        """
        if schema_model is None:
            try:
                from app.models.context import ClientContext
                schema_model = ClientContext
            except ImportError:
                return {"error": "Could not import ClientContext schema."}

        # Try to validate using Pydantic
        try:
            validated = schema_model(**data)
            return validated.dict()
        except Exception as e:
            prompt = (
                "You are a JSON repair agent. The following JSON object does not conform to the schema. "
                "Please repair it so it matches the schema exactly. If you cannot confidently repair a field, leave it empty or null and add a note.\n"
                f"Schema: {schema_model.schema_json()}\n"
                f"Invalid JSON: {data}\n"
                f"Validation error: {str(e)}\n"
                "Return only the repaired JSON object."
            )
            result = await self.agent.run(task=prompt)
            content = result.messages[-1].content
            try:
                return json.loads(content)
            except Exception as e2:
                m = re.search(r'\{[\s\S]*\}', content)
                if m:
                    try:
                        return json.loads(m.group(0))
                    except Exception:
                        pass
                return {"error": f"Failed to parse JSON: {e2}", "raw_response": content}
