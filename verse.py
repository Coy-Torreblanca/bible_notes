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
        """
        Assign metadata for verse object.

        1. Generate _id or metadata if missing (_id or metadata is required).
        2. Get verse text.
        3. Get references of target verse.

        Raises:
            ValueError: If metadata and _id are None.
            ValueError: If no text can be found in the database for the specified verse.
        """
        self.REFERENCE_TEXTS = []

        # Validate required data are present.
        if not self._id and not (self.BOOK, self.VERSE_NUMBER, self.CHAPTER_NUMBER):
            # Chapter/verse/book or _id are required.
            raise ValueError(f"Missing arguments for verse: {self}")

        # If Chapter/verse/book are provided, generate _id.
        if self.BOOK and self.VERSE_NUMBER and self.CHAPTER_NUMBER:
            self._id = f"{self.TRANSLATION}/{self.BOOK}/{self.CHAPTER_NUMBER}/{self.VERSE_NUMBER}"

        # If id is provided generate Chapter/verse/book.
        else:
            data = self._id.split("/")

            if len(data) == 4:
                # Create id using given translation.
                self.TRANSLATION = data[0]
                self.BOOK = data[1]
                self.CHAPTER_NUMBER = int(data[2])
                self.VERSE_NUMBER = int(data[3])

            else:
                # Create id using default translation.
                self.BOOK = data[0]
                self.CHAPTER_NUMBER = int(data[1])
                self.VERSE_NUMBER = int(data[2])
                self._id = f"{self.TRANSLATION}/{self.BOOK}/{self.CHAPTER_NUMBER}/{self.VERSE_NUMBER}"

        # Extract text from database if necessary.
        if not self.VERSE_TEXT:
            # Extract text if only a single verse number was provided.
            if isinstance(self.VERSE_NUMBER, int) or "-" not in self.VERSE_NUMBER:
                self.VERSE_TEXT = MongoDriver.get_client()[self.TRANSLATION][
                    self.BOOK
                ].find_one({"_id": self._id})["VERSE_TEXT"]

            else:
                # Extract the text for start and end verse and every verse in between.
                start_verse, end_verse = self.VERSE_NUMBER.split("-")

                _id_prefix = "/".join(self._id.split("/")[:-1])

                texts = []

                for verse_number in range(int(start_verse), int(end_verse) + 1):
                    text = MongoDriver.get_client()[self.TRANSLATION][
                        self.BOOK
                    ].find_one({"_id": f"{_id_prefix}/{verse_number}"})["VERSE_TEXT"]

                    texts.append(f"{verse_number} - {text}\n")

                # Remove trailing new line.
                texts[-1] = texts[-1][:-1]
                self.VERSE_TEXT = " ".join(texts)

            if not self.VERSE_TEXT:
                raise ValueError(f"No verse text found for specified verse: {self._id}")

        # Extract references from database if not present.
        if not self.REFERENCES:
            self.REFERENCES = []

            # Remove translation from id to query references.
            id_without_translation = "/".join(self._id.split("/")[1:])

            # Get references for this verse.
            references = MongoDriver.get_client()["references"][self.BOOK].find_one(
                {"_id": id_without_translation}, {"references": True}
            )

            if not references:
                references = []

            else:
                references = references.get("references", [])

            # Add reference verses to obj.
            for reference in references:
                self.REFERENCES.append(f"{self.TRANSLATION}/{reference}")

    @classmethod
    def exists(cls, verse_id: str) -> bool:
        """Check if a verse exists in the db with the given verse_id.

        Args:
            verse_id (str): The verse_id of the verse to check if exists.

        Returns:
            bool: If the verse exists.
        """

        try:
            Verse(_id=verse_id)
            return True

        except Exception:
            return False

    def get_reference_texts(self):
        """Get all texts from all reference verses in this obj."""
        self.REFERENCE_TEXTS = []

        for reference in self.REFERENCES:
            # Extract book from reference id for query.
            book = reference.split("/")[1]

            # Get reference text and add to obj.
            self.REFERENCE_TEXTS.append(
                MongoDriver.get_client()[self.TRANSLATION][book].find_one(
                    {"_id": reference}, {"VERSE_TEXT": True}
                )
            )

    def __str__(self, include_references: bool = True) -> str:
        """Create string from verse in markdown syntax.

        Args:
            include_references (bool): Whether to include references in string output. Defaults to True.
                If true and reference texts are present in the obj, reference texts are provided.

        Returns:
            str: Verse in markdown and reference verses with text if requested.
        """
        string = [self._id, self.VERSE_TEXT.replace("\n", "\n>")]

        if not include_references:
            return f"# {string[0]}\n> {string[1]}"

        if self.REFERENCE_TEXTS:
            references = []

            for reference in self.REFERENCE_TEXTS:
                _id = reference["_id"]
                verse_text = reference["VERSE_TEXT"]

                references.append(f"## {_id}\n\n> {verse_text}\n")

            string.append("\n".join(references))

        else:
            string.append("\n".join(self.REFERENCES))

        return f"# {string[0]}\n> {string[1]}\n\n# References\n{string[2]}"

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
