from __future__ import annotations

from typing import Callable, Optional

from attr import define, field, Factory
import openai
from griptape.drivers.image_query.openai_vision_image_query_driver import OpenAiVisionImageQueryDriver


@define
class AzureOpenAiVisionImageQueryDriver(OpenAiVisionImageQueryDriver):
    """Driver for Azure-hosted OpenAI image query API.

    Attributes:
        azure_deployment: An Azure OpenAi deployment id.
        azure_endpoint: An Azure OpenAi endpoint.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_version: An Azure OpenAi API version.
        client: An `openai.AzureOpenAI` client.
    """

    azure_deployment: str = field(
        kw_only=True, default=Factory(lambda self: self.model, takes_self=True), metadata={"serializable": True}
    )
    azure_endpoint: str = field(kw_only=True, metadata={"serializable": True})
    azure_ad_token: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    azure_ad_token_provider: Optional[Callable[[], str]] = field(
        kw_only=True, default=None, metadata={"serializable": False}
    )
    api_version: str = field(default="2024-02-01", kw_only=True, metadata={"serializable": True})
    client: openai.AzureOpenAI = field(
        default=Factory(
            lambda self: openai.AzureOpenAI(
                organization=self.organization,
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.azure_deployment,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            ),
            takes_self=True,
        )
    )
