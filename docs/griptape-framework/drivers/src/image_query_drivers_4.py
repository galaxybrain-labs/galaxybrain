import os

from griptape.drivers import AzureOpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = AzureOpenAiImageQueryDriver(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_2"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_2"],
    model="gpt-4o",
    azure_deployment="gpt-4o",
    max_tokens=256,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

engine.run("Describe the weather in the image", [image_artifact])
