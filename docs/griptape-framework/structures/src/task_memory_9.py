from griptape.structures import Agent
from griptape.tools import CalculatorTool

agent = Agent(
    tools=[
        CalculatorTool()  # Default value of `off_prompt=False` will return the data directly to the LLM
    ]
)
agent.run("What is 10 ^ 3, 55 / 23, and 12345 * 0.5?")
