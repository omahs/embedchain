import os
import unittest
from unittest.mock import MagicMock, patch

from embedchain import App
from embedchain.config import AppConfig, ChatConfig


class TestApp(unittest.TestCase):
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = "test_key"
        self.app = App(config=AppConfig(collect_metrics=False))

    @patch.object(App, "retrieve_from_database", return_value=["Test context"])
    @patch.object(App, "get_answer_from_llm", return_value="Test answer")
    def test_chat_with_memory(self, mock_get_answer, mock_retrieve):
        """
        This test checks the functionality of the 'chat' method in the App class with respect to the chat history
        memory.
        The 'chat' method is called twice. The first call initializes the chat history memory.
        The second call is expected to use the chat history from the first call.

        Key assumptions tested:
            called with correct arguments, adding the correct chat history.
        - After the first call, 'memory.chat_memory.add_user_message' and 'memory.chat_memory.add_ai_message' are
        - During the second call, the 'chat' method uses the chat history from the first call.

        The test isolates the 'chat' method behavior by mocking out 'retrieve_from_database', 'get_answer_from_llm' and
        'memory' methods.
        """
        app = App()
        first_answer = app.chat("Test query 1")
        self.assertEqual(first_answer, "Test answer")
        self.assertEqual(len(app.memory.chat_memory.messages), 2)
        second_answer = app.chat("Test query 2")
        self.assertEqual(second_answer, "Test answer")
        self.assertEqual(len(app.memory.chat_memory.messages), 4)

    @patch("chromadb.api.models.Collection.Collection.add", MagicMock)
    def test_chat_with_where_in_params(self):
        """
        This test checks the functionality of the 'chat' method in the App class.
        It simulates a scenario where the 'retrieve_from_database' method returns a context list based on
        a where filter and 'get_llm_model_answer' returns an expected answer string.

        The 'chat' method is expected to call 'retrieve_from_database' with the where filter  and
        'get_llm_model_answer' methods appropriately and return the right answer.

        Key assumptions tested:
        - 'retrieve_from_database' method is called exactly once with arguments: "Test query" and an instance of
            QueryConfig.
        - 'get_llm_model_answer' is called exactly once. The specific arguments are not checked in this test.
        - 'chat' method returns the value it received from 'get_llm_model_answer'.

        The test isolates the 'chat' method behavior by mocking out 'retrieve_from_database' and
        'get_llm_model_answer' methods.
        """
        with patch.object(self.app, "retrieve_from_database") as mock_retrieve:
            mock_retrieve.return_value = ["Test context"]
            with patch.object(self.app, "get_llm_model_answer") as mock_answer:
                mock_answer.return_value = "Test answer"
                answer = self.app.chat("Test chat", where={"attribute": "value"})

        self.assertEqual(answer, "Test answer")
        self.assertEqual(mock_retrieve.call_args[0][0], "Test chat")
        self.assertEqual(mock_retrieve.call_args[0][2], {"attribute": "value"})
        mock_answer.assert_called_once()

    @patch("chromadb.api.models.Collection.Collection.add", MagicMock)
    def test_chat_with_where_in_chat_config(self):
        """
        This test checks the functionality of the 'chat' method in the App class.
        It simulates a scenario where the 'retrieve_from_database' method returns a context list based on
        a where filter and 'get_llm_model_answer' returns an expected answer string.

        The 'chat' method is expected to call 'retrieve_from_database' with the where filter specified
        in the QueryConfig and 'get_llm_model_answer' methods appropriately and return the right answer.

        Key assumptions tested:
        - 'retrieve_from_database' method is called exactly once with arguments: "Test query" and an instance of
            QueryConfig.
        - 'get_llm_model_answer' is called exactly once. The specific arguments are not checked in this test.
        - 'chat' method returns the value it received from 'get_llm_model_answer'.

        The test isolates the 'chat' method behavior by mocking out 'retrieve_from_database' and
        'get_llm_model_answer' methods.
        """
        with patch.object(self.app, "retrieve_from_database") as mock_retrieve:
            mock_retrieve.return_value = ["Test context"]
            with patch.object(self.app, "get_llm_model_answer") as mock_answer:
                mock_answer.return_value = "Test answer"
                chatConfig = ChatConfig(where={"attribute": "value"})
                answer = self.app.chat("Test chat", chatConfig)

        self.assertEqual(answer, "Test answer")
        self.assertEqual(mock_retrieve.call_args[0][0], "Test chat")
        self.assertEqual(mock_retrieve.call_args[0][1].where, {"attribute": "value"})
        self.assertIsInstance(mock_retrieve.call_args[0][1], ChatConfig)
        mock_answer.assert_called_once()
