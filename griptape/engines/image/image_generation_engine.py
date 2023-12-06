from typing import Optional

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseTextToImageGenerationDriver
from griptape.rules import Ruleset


@define
class TextToImageGenerationEngine:
    text_to_image_generation_driver: BaseTextToImageGenerationDriver = field(kw_only=True)

    def generate_image(
        self,
        prompts: list[str],
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        if not negative_prompts:
            negative_prompts = []

        if rulesets is not None:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        if negative_rulesets is not None:
            for negative_ruleset in negative_rulesets:
                negative_prompts += [rule.value for rule in negative_ruleset.rules]

        return self.text_to_image_generation_driver.generate_image(prompts, negative_prompts=negative_prompts)
