from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import CsvExtractionEngine

# Initialize the CsvExtractionEngine instance
csv_engine = CsvExtractionEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"), column_names=["name", "age", "location"]
)

# Define some unstructured data
sample_text = """
Alice, 28, lives in New
York.
Bob, 35 lives in California
Charlie is 40
Collin is 28 and lives in San Francisco
"""

# Extract CSV rows using the engine
result = csv_engine.extract_text(sample_text)

for row in result:
    print(row.to_text())
