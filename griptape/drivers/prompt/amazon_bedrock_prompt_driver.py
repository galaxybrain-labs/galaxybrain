from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any
import boto3
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.events import CompletionChunkEvent
from .base_multi_model_prompt_driver import BaseMultiModelPromptDriver

if TYPE_CHECKING:
    from griptape.utils import PromptStack


@define
class AmazonBedrockPromptDriver(BaseMultiModelPromptDriver):
    session: boto3.Session = field(default=Factory(lambda: boto3.Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(
            lambda self: self.session.client("bedrock-runtime"),
            takes_self=True,
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        model_input = self.prompt_model_driver.prompt_stack_to_model_input(prompt_stack)
        payload = {
            **self.prompt_model_driver.prompt_stack_to_model_params(prompt_stack),
        }
        if isinstance(model_input, dict):
            payload.update(model_input)

        if self.stream:
            response = self.bedrock_client.invoke_model_with_response_stream(
                modelId=self.model,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(payload),
            )

            response_body = response["body"]
            if response_body:
                tokens = []
                for chunk in response["body"]:
                    decoded_chunk = chunk['chunk']['bytes']
                    decoded_chunk = self.prompt_model_driver.process_output(decoded_chunk).value
                    tokens.append(decoded_chunk)
     
                    if self.structure:
                        self.structure.publish_event(
                            CompletionChunkEvent(token=decoded_chunk)
                        )
                return TextArtifact(value=''.join(tokens))
            else:
                raise Exception("model response is empty")
        else:
            response = self.bedrock_client.invoke_model(
                modelId=self.model,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(payload),
            )

            response_body = response["body"].read()

            if response_body:
                return self.prompt_model_driver.process_output(response_body)
            else:
                raise Exception("model response is empty")
