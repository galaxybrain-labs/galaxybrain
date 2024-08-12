from griptape.drivers import MarkdownifyWebScraperDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import WebScraper

agent = Agent(
    tools=[
        WebScraper(
            web_loader=WebLoader(web_scraper_driver=MarkdownifyWebScraperDriver(timeout=1000)),
            off_prompt=True,
        ),
    ],
)
agent.run("List all email addresses on griptape.ai in a flat numbered markdown list.")
