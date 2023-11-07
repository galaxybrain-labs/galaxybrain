# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/unit-tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**Griptape** is a modular Python framework for building AI-powered applications that connect securely to your enterprise data and APIs. It offers developers the ability to maintain control and flexibility at every step.

**Build AI Apps**: Easily compose apps in Python with modular structures and ready-made tools. Use built-in drivers to connect to whichever LLMs and data stores you choose.

**Control Data Access**: Connect securely to data sources with granular access controls, ensuring LLMs stay focused on the information that matters.

**Scale With Your Workload**: Easily deploy and run apps in the cloud, where your data lives. Process data ahead of time or vectorize it on the fly.

Using Griptape, you can securely integrate with your internal data stores and APIs. You get to control what data goes into the prompt, and what the LLM is allowed to do with it. 

## Documentation

Please refer to [Griptape Docs](https://docs.griptape.ai/) for:

- Getting started guides. 
- Core concepts and design overviews.
- Examples.
- Contribution guidelines.

Please check out [Griptape Trade School](https://learn.griptape.ai/) for free online courses.

## Quick Start

First, install **griptape**:

```
pip install griptape -U
```

Second, configure an OpenAI client by [getting an API key](https://platform.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. By default, Griptape uses [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/gpt/chat-completions-api) to execute LLM prompts.

With Griptape, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. Let's build a simple creative agent that dynamically uses two tools with shared short-term memory.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper, FileManager, ToolOutputProcessor


agent = Agent(
    input_template="Load {{ args[0] }}, summarize it, and store it in a file called {{ args[1] }}.",
    tools=[
        WebScraper(),
        FileManager(),
        ToolOutputProcessor(off_prompt=False)
    ]
)
agent.run("https://griptape.ai", "griptape.txt")
```

And here is the output:
```
[11/02/23 15:28:24] INFO     ToolkitTask 72b89a905be84245a0563b206795ac73       
                             Input: Load https://griptape.ai, summarize it, and 
                             store it in a file called griptape.txt.            
[11/02/23 15:28:37] INFO     Subtask f2cd3cfecaeb4001a0d3eccad32c2d07           
                             Thought: First, I need to use the WebScraper API to
                             load the content of the webpage.                   
                                                                                
                             Action: {"name": "WebScraper", "path":            
                             "get_content", "input": {"values": {"url":         
                             "https://griptape.ai"}}}                           
                    INFO     Subtask f2cd3cfecaeb4001a0d3eccad32c2d07           
                             Response: Output of "WebScraper.get_content" was   
                             stored in memory with memory_name "ToolMemory" and 
                             artifact_namespace                                 
                             "c497d83c1d134db694b9994596016320"                 
[11/02/23 15:28:50] INFO     Subtask 0096dac0f0524636be197e06a37f8aa0           
                             Thought: Now that the webpage content is stored in 
                             memory, I need to use the ToolOutputProcessor API  
                             to summarize the content.                          
                             Action: {"name": "ToolOutputProcessor", "path":   
                             "summarize", "input": {"values": {"memory_name":   
                             "ToolMemory", "artifact_namespace":                
                             "c497d83c1d134db694b9994596016320"}}}              
[11/02/23 15:29:06] INFO     Subtask 0096dac0f0524636be197e06a37f8aa0           
                             Response: Output of "ToolOutputProcessor.summarize"
                             was stored in memory with memory_name "ToolMemory" 
                             and artifact_namespace                             
                             "77584322d33d40e992da9767d02a9018"                 
[11/02/23 15:29:25] INFO     Subtask 7cc3d96500ce4efdac085c07c7370822           
                             Thought: Now that the summary is stored in memory, 
                             I need to use the FileManager API to save the      
                             summary to a file named griptape.txt.              
                             Action: {"name": "FileManager", "path":           
                             "save_memory_artifacts_to_disk", "input":          
                             {"values": {"dir_name": ".", "file_name":          
                             "griptape.txt", "memory_name": "ToolMemory",       
                             "artifact_namespace":                              
                             "77584322d33d40e992da9767d02a9018"}}}              
                    INFO     Subtask 7cc3d96500ce4efdac085c07c7370822           
                             Response: saved successfully                       
[11/02/23 15:29:30] INFO     ToolkitTask 72b89a905be84245a0563b206795ac73       
                             Output: The summary of the webpage                 
                             https://griptape.ai has been successfully stored in
                             a file named griptape.txt.
```

During the run, the Griptape Agent loaded a webpage with a **Tool**, stored its full content in **Tool Memory**, queried it to answer the original question, and finally saved the answer to a file.
The important thing to note here is that no matter how big the webpage is it can never blow up the prompt token limit because the full content never goes back to the main prompt.

[Check out our docs](https://docs.griptape.ai/griptape-framework/structures/prompt-drivers/) to learn more about how to use Griptape with other LLM providers like Anthropic, Claude, Hugging Face, and Azure.

## Versioning

Griptape is in constant development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Thank you for considering contributing to Griptape! Before you start, please read the following guidelines.

### Submitting Issues

If you have identified a bug, want to propose a new feature, or have a question, please submit an issue through our public [issue tracker](https://github.com/griptape-ai/griptape/issues). Before submitting a new issue, please check the existing issues to ensure it hasn't been reported or discussed before.

### Submitting Pull Requests

We welcome and encourage pull requests. To streamline the process, please follow these guidelines:

1. **Existing Issues:** Please submit pull requests only for existing issues. If you want to work on new functionality or fix a bug that hasn't been addressed yet, please first submit an issue. This allows the Griptape team to internally process the request and provide a public response.

2. **Branch:** Submit all pull requests to the `dev` branch. This helps us manage changes and integrate them smoothly.

3. **Unit Tests:** Ensure that your pull request passes all existing unit tests. Additionally, if you are introducing new code, please include new unit tests to validate its functionality.

4. **Documentation:** Every pull request must include a corresponding pull request in the [docs repository](https://github.com/griptape-ai/griptape-docs) or explicitly explain why a documentation update is not required. Documentation is crucial for maintaining a comprehensive and user-friendly project.

## License

Griptape is available under the Apache 2.0 License.
