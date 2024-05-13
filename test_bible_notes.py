import unittest
from datetime import datetime
from bible_notes import BibleNote
from utilities import generate_random_id
from db.driver import MongoDriver


class TestNotes(unittest.TestCase):
    # TODO - Before test create a random id which all new objects should use.
    # TODO - After test delete random ids.
    def setUp(self):
        self.note_id = generate_random_id()
        self.note_id2 = generate_random_id()

    def tearDown(self):
        for note_id in [self.note_id, self.note_id2]:
            MongoDriver.get_client()[BibleNote._MONGO_DATABASE][
                BibleNote._MONGO_COLLECTION
            ].delete_many({"_id": note_id})

            note_id = None

            result = MongoDriver.get_client()[BibleNote._MONGO_DATABASE][
                BibleNote._MONGO_COLLECTION
            ].find_one({"_id": note_id})

        assert result is None

    def test_database_driver(self):
        """Test object database drivers."""

        # Create new object.
        original_note = BibleNote(
            _id=self.note_id,
            note_text="This is a note.",
            theme="theme",
            tags={"one", "two", "three"},
            key_value_tags={"key": "value"},
            referenced_verses={"asv/John/1/1"},
        )

        # Insert object.
        original_note.upsert()

        self.assertEqual(datetime.now().date(), original_note.date_created.date())
        self.assertEqual(datetime.now().date(), original_note.date_updated.date())

        # Get object.
        object_from_db = BibleNote.get(original_note._id)

        self.assertEqual(datetime.now().date(), object_from_db.date_created.date())
        self.assertEqual(datetime.now().date(), object_from_db.date_updated.date())

        # Don't test date attributes in object equality test.
        # It is an automatic value which changes when an object is inserted in the database.
        original_note.date_updated = None
        original_note.date_created = None
        object_from_db.date_updated = None
        object_from_db.date_created = None

        # Validate gotten object is the same as inserted object.
        self.assertEqual(original_note, object_from_db)

        # Update object attribute and upsert it.
        object_from_db.tags = {"new_tag"}
        object_from_db.upsert()

        # Get updated object.
        object_from_db_two = BibleNote.get(object_from_db._id)

        self.assertEqual(datetime.now().date(), object_from_db_two.date_created.date())
        self.assertEqual(datetime.now().date(), object_from_db_two.date_updated.date())

        # Don't test date attributes in object equality test.
        # It is an automatic value which changes when an object is inserted in the database.
        object_from_db.date_updated = None
        object_from_db.date_created = None
        object_from_db_two.date_updated = None
        object_from_db_two.date_created = None

        # Ensure new object is the same as updated object.
        self.assertEqual(object_from_db, object_from_db_two)

        # Ensure new object is not the same as original.
        self.assertNotEqual(original_note, object_from_db_two)

        # Ensure attribute was updated.
        self.assertEqual(object_from_db_two.tags, {"new_tag"})

        # Ensure all _id fields are equal.
        self.assertEqual(original_note._id, object_from_db._id)
        self.assertEqual(original_note._id, object_from_db_two._id)

        # Delete object.
        BibleNote.delete(original_note._id)

        # Ensure get returns None.
        self.assertIsNone(BibleNote.get(object_from_db._id))

    def test_data_validation(self):
        """Ensure that non-valid BibleNote objects cannot be upserted."""

        # Ensure no object without a required attribute may be upserted into the database.
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

        # Ensure bible notes with invalid note references cannot be inserted.
        invalid_bible_note = BibleNote(
            _id=self.note_id,
            note_text="asdf",
            theme="asdf",
            tags=["asdf"],
            referenced_notes=["invalid_note_id"],
        )

        try:
            invalid_bible_note.upsert()
            self.fail(f"Invalid bible note successfully upserted: {invalid_bible_note}")

        except ValueError:
            pass

        # Ensure bible notes with invalid verse references cannot be inserted.
        invalid_bible_note = BibleNote(
            _id=self.note_id,
            note_text="asdf",
            theme="asdf",
            tags=["asdf"],
            referenced_verses=["invalid_verse_id"],
        )

        try:
            invalid_bible_note.upsert()
            self.fail(f"Invalid bible note successfully upserted: {invalid_bible_note}")

        except ValueError:
            pass

    def test_deletion_of_references(self):
        """Ensure when a note referenced by another is deleted, the reference is deleted."""

        # Create note that will be referenced by another.
        referenced_note = BibleNote(
            _id=self.note_id, theme="askdfl", note_text="asdf", tags=["asdf"]
        )

        referenced_note.upsert()

        # Create note that references the original.
        referencing_note = BibleNote(
            _id=self.note_id2,
            theme="askdfl",
            note_text="asdf",
            tags=["asdf"],
            referenced_notes=[self.note_id],
        )

        referencing_note.upsert()

        # Delete referenced note.
        BibleNote.delete(self.note_id)

        # Refresh referencing note.
        referencing_note = BibleNote.get(self.note_id2)

        # Ensure deleted note no longer is referenced.
        self.assertEqual(referencing_note.referenced_notes, set())

    def test_valid_refences(self):
        """Ensure valid refences can be upserted."""

        # Create note that will be referenced by another.
        referenced_note = BibleNote(
            _id=self.note_id, theme="askdfl", note_text="asdf", tags=["asdf"]
        )

        referenced_note.upsert()

        # Create note that references the original.
        referencing_note = BibleNote(
            _id=self.note_id2,
            theme="askdfl",
            note_text="asdf",
            tags=["asdf"],
            referenced_notes=[self.note_id],
        )

        referencing_note.upsert()


if __name__ == "__main__":
    unittest.main()
