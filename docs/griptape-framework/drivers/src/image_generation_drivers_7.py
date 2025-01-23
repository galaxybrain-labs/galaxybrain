from griptape.artifacts import TextArtifact
from griptape.drivers.image_generation.huggingface_pipeline import HuggingFacePipelineImageGenerationDriver
from griptape.drivers.image_generation_pipeline.stable_diffusion_3 import StableDiffusion3ImageGenerationPipelineDriver
from griptape.structures import Pipeline
from griptape.tasks import PromptImageGenerationTask

image_generation_task = PromptImageGenerationTask(
    input=TextArtifact("landscape photograph, verdant, countryside, 8k"),
    image_generation_driver=HuggingFacePipelineImageGenerationDriver(
        model="stabilityai/stable-diffusion-3-medium-diffusers",
        device="cuda",
        pipeline_driver=StableDiffusion3ImageGenerationPipelineDriver(
            height=512,
            width=512,
        ),
    ),
)

output_artifact = Pipeline(tasks=[image_generation_task]).run().output
