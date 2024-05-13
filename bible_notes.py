from datetime import datetime
from typing import Optional
from verse import Verse
from utilities import generate_random_id
from db.driver import MongoDriver
from dataclasses import dataclass, field, asdict


@dataclass
class BibleNote:
    """Object to write, update, and search notes related to the Bible.

    Required data for database upsertion:
        _id,
        note_text,
        theme,
        tags,
    """

    # Mongo Driver Attributes.
    _MONGO_DATABASE = "notes"
    _MONGO_COLLECTION = "all_notes"

    # If not provided, presumed to be a new note and id will be generated.
    # The _id field in the Mongo database.
    _id: str = None
    # Text of note containing referenced_verses and referenced_notes.
    note_text: str = None
    # Summary of note_text.
    theme: str = None
    # Tags describing Note.
    key_value_tags: list[dict] = field(default_factory=lambda: {})
    tags: set[str] = field(default_factory=lambda: [])

    date_updated: Optional[datetime] = None
    date_created: Optional[datetime] = None

    # List of verses referenced in this note.
    # Values should be verse_ids.
    referenced_verses: set[str] = field(default_factory=lambda: set())
    # Set of notes referenced in this note.
    # Values should be note_ids.
    referenced_notes: set[str] = field(default_factory=lambda: set())

    def __post_init__(self):
        """
        Generate _id. Removed deleted referenced notes from note text.
        Note - If you need existing note, use the get method.
        """

        # Create note_id if one not provided.
        new_note = self._id is None

        if new_note:
            self._id = generate_random_id()

        else:
            # Remove deleted referenced notes from note text.
            current_note_references = self.get_note_references()

            for referenced_note_id in self.referenced_notes:
                if referenced_note_id not in current_note_references:
                    # Deleted note is referenced in text.
                    # Delete note referenced in text.
                    self.delete_note_reference_from_text(referenced_note_id)

    def update_note_text(self):
        """Update note text and dependent attributes."""
        pass

    def get_note_references(self) -> set:
        """Parse note text for referenced notes.

        Returns:
            set: Referenced notes in note text.
        """
        return set()

    def delete_note_reference_from_text(self, note_id: str) -> None:
        """Delete referenced note in note text.

        Args:
            note_id (str): Note id to delete from note text.
        """
        pass

    @classmethod
    def get(cls, _id: str) -> Optional["BibleNote"]:
        """From the database, get the object represented by the given note_id.

        Returns:
            Note or None: Return None if there is no data related to the note_id provided.
                          Otherwise, provide the given Note object associated with the note_id.
        """
        data = MongoDriver.get_client()["notes"]["all_notes"].find_one({"_id": _id})

        if not data:
            return None

        data["referenced_verses"] = set(data["referenced_verses"])
        data["referenced_notes"] = set(data["referenced_notes"])
        data["tags"] = set(data["tags"])

        return cls(**data)

    @classmethod
    def delete(cls, _id: str) -> bool:
        """Delete the document associated with the note_id from the database.
        Delete references to note_id.

        Args:
            _id (str): The note_id of the document to delete.

        Returns:
            bool: If the document was deleted.
        """

        # Delete references to note.
        MongoDriver.get_client()[cls._MONGO_DATABASE][
            cls._MONGO_COLLECTION
        ].update_many({}, {"$pull": {"referenced_notes": _id}})

        # Delete Note.
        result = MongoDriver.get_client()[cls._MONGO_DATABASE][
            cls._MONGO_COLLECTION
        ].delete_one({"_id": _id})

        return result.deleted_count == 1

    @classmethod
    def exists(cls, note_id: str) -> bool:
        """Check if a note exists with the given note_id.

        Args:
            note_id (str): The note_id of the note to check if exists.

        Returns:
            bool: If the note exists.
        """

        return (
            MongoDriver.get_client()[cls._MONGO_DATABASE][
                cls._MONGO_COLLECTION
            ].count_documents({"_id": note_id})
            == 1
        )

    def upsert(self) -> None:
        """Upsert this object into the database.
           Validate required fields are present before upserting.

        Raises:
            ValueError: If required fields are not present.
        """

        # Ensure all required fields are present.
        if not self._id or not self.note_text or not self.theme or not self.tags:
            raise ValueError("Required data not present in Object.")

        # Ensure all references exist.
        for note_id in self.referenced_notes:
            if not BibleNote.exists(note_id=note_id):
                raise ValueError(
                    f"Attempting to reference a non-existing note. Note_id: {note_id}"
                )

        for verse_id in self.referenced_verses:
            if not Verse.exists(verse_id=verse_id):
                raise ValueError(
                    f"Attempting to reference a non-existing verse. verse_id: {verse_id}"
                )

        # Update date updated.
        self.date_updated = datetime.now()

        if not self.date_created:
            self.date_created = datetime.now()

        # Upsert object.
        self_dict = self.to_db_dict()

        # Convert sets to lists as Mongo does not accept lists.
        self_dict["referenced_verses"] = list(self_dict["referenced_verses"])
        self_dict["referenced_notes"] = list(self_dict["referenced_notes"])
        self_dict["tags"] = list(self_dict["tags"])

        MongoDriver.get_client()[self._MONGO_DATABASE][
            self._MONGO_COLLECTION
        ].update_one(
            filter={"_id": self_dict["_id"]},
            update={"$set": self_dict},
            upsert=True,
        )

    def to_db_dict(self) -> dict:
        """Create a dictionary version of this object

        Returns:
            dict: dictionary version of this object.
        """

        self_dict = asdict(self)

        return self_dict
