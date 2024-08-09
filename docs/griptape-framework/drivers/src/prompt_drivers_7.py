import os

from griptape.drivers import AnthropicPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=AnthropicPromptDriver(
        model="claude-3-opus-20240229",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
)

agent.run("Where is the best place to see cherry blossums in Japan?")
