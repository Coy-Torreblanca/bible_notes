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
    REFERENCES: list[str] = field(default_factory=lambda: [])
    _id: str = field(default=None)

    def __post_init__(self):
        self.REFERENCE_TEXTS = []

        # Chapter/verse/book or _id are required.
        if not self._id and not (self.BOOK, self.VERSE_NUMBER, self.CHAPTER_NUMBER):
            raise ValueError(f"Missing arguments for verse: {self}")

        # If Chapter/verse/book are provided, generate _id.
        if self.BOOK and self.VERSE_NUMBER and self.CHAPTER_NUMBER:
            self._id = f"{self.TRANSLATION}/{self.BOOK}/{self.CHAPTER_NUMBER}/{self.VERSE_NUMBER}"

        # If id is provided generate Chapter/verse/book.
        else:
            data = self._id.split("/")

            # Parse non ids with translations and without translations.
            if len(data) == 4:
                self.TRANSLATION = data[0]
                self.BOOK = data[1]
                self.CHAPTER_NUMBER = int(data[2])
                self.VERSE_NUMBER = int(data[3])

            else:
                self.BOOK = data[0]
                self.CHAPTER_NUMBER = int(data[1])
                self.VERSE_NUMBER = int(data[2])
                self._id = f"{self.TRANSLATION}/{self.BOOK}/{self.CHAPTER_NUMBER}/{self.VERSE_NUMBER}"

        # Extract text from database if necessary.
        if not self.VERSE_TEXT:
            self.VERSE_TEXT = MongoDriver.get_client()[self.TRANSLATION][
                self.BOOK
            ].find_one({"_id": self._id})["VERSE_TEXT"]

            if not self.VERSE_TEXT:
                raise ValueError(f"No verse text found for specified verse: {self._id}")

        if not self.REFERENCES:
            self.REFERENCES = []
            id_without_translation = "/".join(self._id.split("/")[1:])
            references = MongoDriver.get_client()["references"][self.BOOK].find_one(
                {"_id": id_without_translation}, {"references": True}
            )

            if not references:
                references = []

            else:
                references = references.get("references", [])

            for reference in references:
                self.REFERENCES.append(f"{self.TRANSLATION}/{reference}")

    def get_reference_texts(self):
        self.REFERENCE_TEXTS = []

        for reference in self.REFERENCES:
            book = reference.split("/")[1]

            self.REFERENCE_TEXTS.append(
                MongoDriver.get_client()[self.TRANSLATION][book].find_one(
                    {"_id": reference}, {"VERSE_TEXT": True}
                )
            )

    def __str__(self) -> str:
        string = [self._id, self.VERSE_TEXT]

        if self.REFERENCE_TEXTS:
            references = []

            for reference in self.REFERENCE_TEXTS:
                _id = reference["_id"]
                verse_text = reference["VERSE_TEXT"]

                references.append(f"## {_id}\n\n> {verse_text}\n")

            string.append("\n".join(references))

        else:
            string.append("\n".join(self.REFERENCES))

        return f"# Verse\n{string[0]}\n\n# Text\n> {string[1]}\n\n# References\n{string[2]}"

    def todict(self):
        return asdict(self)

    # TODO
    # Create verse object(s) from text.
    # In the future should use vector search.

    # TODO
    # Create a list of verses given:
    # f"{TRANSLATION}/{BOOK}/{CHAPTER_NUMBER}/{VERSE_NUMBER}-{VERSE_NUMBER}"
    # f"{TRANSLATION}/{BOOK}/{CHAPTER_NUMBER}/{VERSE_NUMBER}-{CHAPTER_NUMBER}/{VERSE_NUMBER}"


if __name__ == "__main__":
    Verse("Genesis", 1, 1).get_reference_texts()
