import pytest

from griptape.config import OpenAiDriverConfig


class TestOpenAiStructureConfig:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("openai.OpenAI")

    @pytest.fixture()
    def config(self):
        return OpenAiDriverConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "OpenAiDriverConfig",
            "prompt": {
                "type": "OpenAiChatPromptDriver",
                "base_url": None,
                "model": "gpt-4o",
                "organization": None,
                "response_format": None,
                "seed": None,
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "user": "",
                "use_native_tools": True,
            },
            "conversation_memory": None,
            "embedding": {
                "base_url": None,
                "model": "text-embedding-3-small",
                "organization": None,
                "type": "OpenAiEmbeddingDriver",
            },
            "image_generation": {
                "api_version": None,
                "base_url": None,
                "image_size": "512x512",
                "model": "dall-e-2",
                "organization": None,
                "quality": "standard",
                "response_format": "b64_json",
                "style": None,
                "type": "OpenAiImageGenerationDriver",
            },
            "image_query": {
                "api_version": None,
                "base_url": None,
                "image_quality": "auto",
                "max_tokens": 256,
                "model": "gpt-4o",
                "organization": None,
                "type": "OpenAiImageQueryDriver",
            },
            "vector_store": {
                "embedding_driver": {
                    "base_url": None,
                    "model": "text-embedding-3-small",
                    "organization": None,
                    "type": "OpenAiEmbeddingDriver",
                },
                "type": "LocalVectorStoreDriver",
            },
            "text_to_speech": {
                "type": "OpenAiTextToSpeechDriver",
                "api_version": None,
                "base_url": None,
                "format": "mp3",
                "model": "tts",
                "organization": None,
                "voice": "alloy",
            },
            "audio_transcription": {
                "type": "OpenAiAudioTranscriptionDriver",
                "api_version": None,
                "base_url": None,
                "model": "whisper-1",
                "organization": None,
            },
        }

    def test_from_dict(self, config):
        assert OpenAiDriverConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
