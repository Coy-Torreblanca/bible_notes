from enum import Enum
from dataclasses import dataclass, field, asdict
from db.driver import MongoDriver


@dataclass
class Verse:
    BOOK: str
    CHAPTER_NUMBER: int
    VERSE_NUMBER: int
    VERSE_TEXT: str = field(default="")
    # TODO Make default transaction configurable.
    TRANSLATION: str = field(default="asv")
    _id: str = field(default=None)

    def __post_init__(self):
        self._id = (
            f"{self.TRANSLATION}/{self.BOOK}/{self.CHAPTER_NUMBER}/{self.VERSE_NUMBER}"
        )

        if not self.VERSE_TEXT:
            self.VERSE_TEXT = MongoDriver.get_client()[self.TRANSLATION][
                self.BOOK
            ].find_one({"_id": self._id})["VERSE_TEXT"]

    def todict(self):
        return asdict(self)

    # TODO
    # Generate ID given required items. (Default translation possible.)

    # TODO
    # Create verse object(s) from text.
    # In the future should use vector search.

    # TODO
    # Create a list of verses given:
    # f"{TRANSLATION}/{BOOK}/{CHAPTER_NUMBER}/{VERSE_NUMBER}-{VERSE_NUMBER}"
    # f"{TRANSLATION}/{BOOK}/{CHAPTER_NUMBER}/{VERSE_NUMBER}-{CHAPTER_NUMBER}/{VERSE_NUMBER}"
