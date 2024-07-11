import boto3
from pytest import fixture
from griptape.config import AmazonBedrockStructureConfig
from tests.utils.aws import mock_aws_credentials


class TestAmazonBedrockStructureConfig:
    @fixture(autouse=True)
    def run_before_and_after_tests(self):
        mock_aws_credentials()

    @fixture
    def config(self):
        mock_aws_credentials()
        return AmazonBedrockStructureConfig()

    @fixture
    def config_with_values(self):
        return AmazonBedrockStructureConfig(
            session=boto3.Session(
                aws_access_key_id="testing", aws_secret_access_key="testing", region_name="region-value"
            )
        )

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "conversation_memory_driver": None,
            "embedding_driver": {"model": "amazon.titan-embed-text-v1", "type": "AmazonBedrockTitanEmbeddingDriver"},
            "image_generation_driver": {
                "image_generation_model_driver": {
                    "cfg_scale": 7,
                    "outpainting_mode": "PRECISE",
                    "quality": "standard",
                    "type": "BedrockTitanImageGenerationModelDriver",
                },
                "image_height": 512,
                "image_width": 512,
                "model": "amazon.titan-image-generator-v1",
                "seed": None,
                "type": "AmazonBedrockImageGenerationDriver",
            },
            "image_query_driver": {
                "type": "AmazonBedrockImageQueryDriver",
                "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "max_tokens": 256,
                "image_query_model_driver": {"type": "BedrockClaudeImageQueryModelDriver"},
            },
            "prompt_driver": {
                "max_tokens": None,
                "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "stream": False,
                "temperature": 0.1,
                "type": "AmazonBedrockPromptDriver",
                "tool_choice": {"auto": {}},
                "use_native_tools": True,
            },
            "vector_store_driver": {
                "embedding_driver": {
                    "model": "amazon.titan-embed-text-v1",
                    "type": "AmazonBedrockTitanEmbeddingDriver",
                },
                "type": "LocalVectorStoreDriver",
            },
            "type": "AmazonBedrockStructureConfig",
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert AmazonBedrockStructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_from_dict_with_values(self, config_with_values):
        assert (
            AmazonBedrockStructureConfig.from_dict(config_with_values.to_dict()).to_dict()
            == config_with_values.to_dict()
        )

    def test_to_dict_with_values(self, config_with_values):
        assert config_with_values.to_dict() == {
            "conversation_memory_driver": None,
            "embedding_driver": {"model": "amazon.titan-embed-text-v1", "type": "AmazonBedrockTitanEmbeddingDriver"},
            "image_generation_driver": {
                "image_generation_model_driver": {
                    "cfg_scale": 7,
                    "outpainting_mode": "PRECISE",
                    "quality": "standard",
                    "type": "BedrockTitanImageGenerationModelDriver",
                },
                "image_height": 512,
                "image_width": 512,
                "model": "amazon.titan-image-generator-v1",
                "seed": None,
                "type": "AmazonBedrockImageGenerationDriver",
            },
            "image_query_driver": {
                "type": "AmazonBedrockImageQueryDriver",
                "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "max_tokens": 256,
                "image_query_model_driver": {"type": "BedrockClaudeImageQueryModelDriver"},
            },
            "prompt_driver": {
                "max_tokens": None,
                "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "stream": False,
                "temperature": 0.1,
                "type": "AmazonBedrockPromptDriver",
                "tool_choice": {"auto": {}},
                "use_native_tools": True,
            },
            "vector_store_driver": {
                "embedding_driver": {
                    "model": "amazon.titan-embed-text-v1",
                    "type": "AmazonBedrockTitanEmbeddingDriver",
                },
                "type": "LocalVectorStoreDriver",
            },
            "type": "AmazonBedrockStructureConfig",
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }
        assert config_with_values.session.region_name == "region-value"
