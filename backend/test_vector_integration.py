import unittest
import chromadb

from uuid import uuid4
from unittest.mock import patch

from vector_memory import (
    save_embedding,
    search_semantic_memory,
    delete_persona_memories,
)


class VectorMemoryIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = chromadb.EphemeralClient()

        self.collection = self.client.create_collection(
            name=f"test_memories_{uuid4().hex}"
        )

    def tearDown(self):
        self.client.delete_collection(name=self.collection.name)

    def test_persona_memory_isolation(self):
        with patch("vector_memory.collection", self.collection):
            with patch("vector_memory.get_embedding", return_value=[0.1, 0.2, 0.3]):
                # Save memories from two different personas
                save_embedding(1, "I love cricket", 5)
                save_embedding(2, "I love football", 12)

                # search persona memories for persona 5
                results = search_semantic_memory(
                    question="Favorite sport?", persona_id=5, n_results=3
                )

                self.assertIn("I love cricket", results)
                self.assertNotIn("I love football", results)

    def test_delete_persona_memory(self):
        with patch("vector_memory.collection", self.collection):
            with patch("vector_memory.get_embedding", return_value=[0.1, 0.2, 0.3]):

                # Arrange
                save_embedding(1, "I love cricket", 5)
                save_embedding(2, "I love football", 12)

                # Act
                delete_persona_memories(persona_id=5)

                # Assert
                self.assertEqual(self.collection.count(), 1)

                results = search_semantic_memory(
                    question="Favorite sport?", persona_id=12, n_results=3
                )

                self.assertEqual(results, ["I love football"])

                deleted_memories = self.collection.get(where={"persona_id": 5})

                self.assertEqual(deleted_memories["ids"], [])
