from __future__ import annotations

import base64

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationModelDriver


@define
class BedrockTitanImageGenerationModelDriver(BaseImageGenerationModelDriver):
    """Image Generation Model Driver for Amazon Bedrock Titan Image Generator.

    Attributes:
        task_type: The type of image generation task to perform, defaults to TEXT_IMAGE (text-to-image).
        quality: The quality of the generated image, defaults to standard.
        cfg_scale: Specifies how strictly image generation follows the provided prompt. Defaults to 7, (1.0 to 10.0].
    """

    task_type: str = field(default="TEXT_IMAGE", kw_only=True)
    quality: str = field(default="standard", kw_only=True)
    cfg_scale: int = field(default=7, kw_only=True)

    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": self.task_type,
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": self.quality,
                "width": image_width,
                "height": image_height,
                "cfgScale": self.cfg_scale,
            },
        }

        if negative_prompts:
            request["textToImageParams"]["negativeText"] = ", ".join(negative_prompts)

        if seed:
            request["imageGenerationConfig"]["seed"] = seed

        return request

    def image_variation_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__} does not support variation")

    def image_inpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__} does not support inpainting")

    def image_outpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__} does not support outpainting")

    def get_generated_image(self, response: dict) -> bytes:
        b64_image_data = response["images"][0]

        return base64.decodebytes(bytes(b64_image_data, "utf-8"))
