import pytest
from unittest import mock
from griptape.drivers import AmazonBedrockEmbeddingDriver


class TestAmazonBedrockEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        fake_embeddings = '{"embedding": [0, 1, 0]}'
        
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_embeddings
        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    def test_init(self):
        assert AmazonBedrockEmbeddingDriver()

    def test_try_embed_string(self):
        assert AmazonBedrockEmbeddingDriver().try_embed_string(
            "foobar"
        ) == [0, 1, 0]
