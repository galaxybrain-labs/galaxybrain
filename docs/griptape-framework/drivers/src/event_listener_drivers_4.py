import os

from griptape.config import config
from griptape.config.drivers import DriverConfig
from griptape.drivers import AwsIotCoreEventListenerDriver, OpenAiChatPromptDriver
from griptape.events import EventListener, FinishStructureRunEvent, event_bus
from griptape.rules import Rule
from griptape.structures import Agent

config.driver_config = DriverConfig(prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo", temperature=0.7))
event_bus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=AwsIotCoreEventListenerDriver(
                topic=os.environ["AWS_IOT_CORE_TOPIC"],
                iot_endpoint=os.environ["AWS_IOT_CORE_ENDPOINT"],
            ),
        ),
    ]
)

agent = Agent(
    rules=[Rule(value="You will be provided with a text, and your task is to extract the airport codes from it.")],
)

agent.run("I want to fly from Orlando to Boston")
