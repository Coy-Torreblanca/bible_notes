from enum import Enum
from dataclasses import dataclass, field, asdict
from db.driver import MongoDriver


@dataclass
class Verse:
    BOOK: str = field(default="")
    CHAPTER_NUMBER: int = field(default=None)
    VERSE_NUMBER: int = field(default=None)
    VERSE_TEXT: str = field(default="")
    # TODO Make default transaction configurable.
    TRANSLATION: str = field(default="asv")
    _id: str = field(default=None)

    def __post_init__(self):
        if not self._id and not (self.BOOK, self.VERSE_NUMBER, self.CHAPTER_NUMBER):
            raise ValueError(f"Missing arguments for verse: {self}")

        if self.BOOK and self.VERSE_NUMBER and self.CHAPTER_NUMBER:
            self._id = f"{self.TRANSLATION}/{self.BOOK}/{self.CHAPTER_NUMBER}/{self.VERSE_NUMBER}"

        else:
            data = self._id.split("/")
            self.TRANSLATION = data[0]
            self.BOOK = data[1]
            self.CHAPTER_NUMBER = data[2]
            self.VERSE_NUMBER = data[3]

        if not self.VERSE_TEXT:
            self.VERSE_TEXT = MongoDriver.get_client()[self.TRANSLATION][
                self.BOOK
            ].find_one({"_id": self._id})["VERSE_TEXT"]

            if not self.VERSE_TEXT:
                raise ValueError(f"No verse text found for specified verse: {_id}")

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
