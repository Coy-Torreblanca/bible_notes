import re
from typing import Union, Optional
from verse import Verse
from utilities import generate_random_id
from db.driver import MongoDriver
from dataclasses import dataclass, field, asdict


@dataclass
class BibleNote:
    """Object to write, update, and search notes related to the Bible.

    Required data for database upsertion:
        _id
        note_text
        theme
        tags
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
    tags: list[str] = field(default_factory=lambda: [])

    # List of verses referenced in this note.
    # If any are string, assumed to be verse_id and will be converted into a verse.
    referenced_verses: list[Union[Verse, str]] = field(default_factory=lambda: [])
    # List of notes referenced in this note.
    # If any are string, assumed to be _id and will be converted into a verse.
    referenced_notes: list[Union["BibleNote", str]] = field(default_factory=lambda: [])

    def __post_init__(self):
        """
        1. Create _id if one not provided.
        2. Convert verse_ids and note_ids into respective objects.
        """

        # Create note_id if one not provided.
        self._id = self._id if self._id else generate_random_id()

        # Convert note_ids into Note objects.
        for i in range(len(self.referenced_notes)):
            if isinstance(self.referenced_notes[i], str):
                self.referenced_notes[i] = BibleNote(_id=self.referenced_notes[i])

        # Convert verse_ids into Verse objects.
        for i in range(len(self.referenced_verses)):
            if isinstance(self.referenced_verses[i], str):
                self.referenced_verses[i] = Verse(_id=self.referenced_verses[i])

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

        return cls(**data)

    @classmethod
    def delete(cls, _id: str) -> bool:
        """Delete the document associated with the note_id from the database.

        Args:
            _id (str): The note_id of the document to delete.

        Returns:
            bool: If the document was deleted.
        """

        result = MongoDriver.get_client()[cls._MONGO_DATABASE][
            cls._MONGO_COLLECTION
        ].delete_one({"_id": _id})

        return result.deleted_count == 1

    def upsert(self) -> None:
        """Upsert this object into the database.
           Validate required fields are present before upserting.

        Raises:
            ValueError: If required fields are not present.
        """

        # Validate data.
        if not self._id or not self.note_text or not self.theme or not self.tags:
            raise ValueError("Required data not present in Object.")

        self_dict = self.to_db_dict()
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
            dict: _description_
        """

        self_dict = asdict(self)

        # Convert child objects into their ids.
        # TODO - (presumebly) spent compute power converting objects to dictionaries only to convert them back to strings.
        self_dict["referenced_verses"] = [verse._id for verse in self.referenced_verses]
        self_dict["referenced_notes"] = [note._id for note in self.referenced_notes]

        return self_dict
