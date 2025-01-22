import os

from griptape.drivers.web_search.tavily import TavilyWebSearchDriver

driver = TavilyWebSearchDriver(api_key=os.environ["TAVILY_API_KEY"])

driver.search("griptape ai")
