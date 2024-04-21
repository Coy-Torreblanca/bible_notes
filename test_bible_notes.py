import unittest
from bible_notes import BibleNote
from utilities import generate_random_id
from db.driver import MongoDriver


class TestNotes(unittest.TestCase):
    # TODO - Before test create a random id which all new objects should use.
    # TODO - After test delete random ids.
    def setUp(self):
        self.note_id = generate_random_id()

    def tearDown(self):
        MongoDriver.get_client()[BibleNote._MONGO_DATABASE][
            BibleNote._MONGO_COLLECTION
        ].delete_many({"_id": self.note_id})

        self.note_id = None

        result = MongoDriver.get_client()[BibleNote._MONGO_DATABASE][
            BibleNote._MONGO_COLLECTION
        ].find_one({"_id": self.note_id})

        assert result is None

    def test_database_driver(self):
        """Test object database drivers."""

        # Create new object.
        original_note = BibleNote(
            _id=self.note_id,
            note_text="This is a note.",
            theme="theme",
            tags=["tag"],
            referenced_notes=["asjldfja"],
            referenced_verses=["asv/John/1/1"],
        )

        # Insert object.
        original_note.upsert()

        # Get object.
        object_from_db = BibleNote.get(original_note._id)

        # Validate gotten object is the same as inserted object.
        self.assertEqual(original_note, object_from_db)

        # Update object attribute and upsert it.
        object_from_db.tags = ["new_tag"]
        object_from_db.upsert()

        # Get updated object.
        object_from_db_two = BibleNote.get(object_from_db._id)

        # Ensure new object is the same as updated object.
        self.assertEqual(object_from_db, object_from_db_two)

        # Ensure new object is not the same as original.
        self.assertNotEqual(original_note, object_from_db_two)

        # Ensure attribute was updated.
        self.assertEqual(object_from_db_two.tags, ["new_tag"])

        # Ensure all _id fields are equal.
        self.assertEqual(original_note._id, object_from_db._id)
        self.assertEqual(original_note._id, object_from_db_two._id)

        # Delete object.
        BibleNote.delete(original_note._id)

        # Ensure get returns None.
        self.assertIsNone(BibleNote.get(object_from_db._id))

    def test_data_validation(self):
        """Ensure that non-valid BibleNote objects cannot be upserted."""

        invalid_bible_notes = [
            BibleNote(_id=self.note_id, note_text="asdf", theme="asdf"),
            BibleNote(_id=self.note_id, theme="asdf", tags=["asdf"]),
            BibleNote(_id=self.note_id, tags=["sdf"], note_text="asdf"),
        ]

        for invalid_bible_note in invalid_bible_notes:
            try:
                invalid_bible_note.upsert()
                self.fail(
                    f"Invalid bible note successfully upserted: {invalid_bible_note}"
                )

            except ValueError:
                pass


if __name__ == "__main__":
    unittest.main()