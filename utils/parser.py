import json
from langchain_core.output_parsers import JsonOutputParser


class CustomJsonOutputParser(JsonOutputParser):
    def get_schema_json(self):
        schema = dict(self._get_schema(self.pydantic_object).items())
        reduced_schema = schema
        schema_str = json.dumps(reduced_schema, ensure_ascii=False)
        schema_str_escaped = schema_str.replace("{", "{{").replace("}", "}}")
        return f"""
        OUTPUT JSON SCHEMA:
        {schema_str_escaped}
        """