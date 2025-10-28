
import re
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class ValidatorAgent:
    def __init__(self, name="validator", system_message="Validates and repairs JSON output using schema."):
        self.model_client = OpenAIChatCompletionClient(model="gpt-4o")
        self.agent = AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    def validate(self, data: dict, schema_model=None):
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
            # If validation fails, use GPT-4o to repair
            prompt = (
                "You are a JSON repair agent. The following JSON object does not conform to the schema. "
                "Please repair it so it matches the schema exactly. If you cannot confidently repair a field, leave it empty or null and add a note.\n"
                f"Schema: {schema_model.schema_json()}\n"
                f"Invalid JSON: {data}\n"
                f"Validation error: {str(e)}\n"
                "Return only the repaired JSON object."
            )
            response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
            try:
                match = re.search(r'{[\s\S]+}', response)
                if match:
                    return json.loads(match.group(0))
                else:
                    raise ValueError("No JSON object found in response.")
            except Exception as e2:
                return {"error": str(e2), "raw_response": response}
