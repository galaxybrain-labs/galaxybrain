from schema import Schema

from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import JsonExtractionEngine
from griptape.structures import Agent
from griptape.tasks import ExtractionTask

# Instantiate the json extraction engine
json_extraction_engine = JsonExtractionEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
    template_schema=Schema({"users": [{"name": str, "age": int, "location": str}]}).json_schema("UserSchema"),
)

# Define some unstructured data and a schema
json_data = """
Alice (Age 28) lives in New York.
Bob (Age 35) lives in California.
"""

agent = Agent()
agent.add_task(
    ExtractionTask(
        extraction_engine=json_extraction_engine,
    )
)

# Run the agent
agent.run(json_data)
