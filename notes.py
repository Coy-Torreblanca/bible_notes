import re
from verse import Verse
from db.driver import MongoDriver
from dataclasses import dataclass, field, asdict


@dataclass
class Note:
    note: str = field(default="")
    verses: list[Verse] = field(default_factory=lambda: [])

    VERSE_REGEX = "@([a-zA-z]+/[0-9]+/[0-9]+)"

    def __post_init__(self):
        self.extract_from_text(self.note)

    def extract_from_text(self, text: str) -> "Note":
        verses = []
        matches = re.findall(self.VERSE_REGEX, text)

        for match in matches:
            verses.append(Verse(_id=match))

        self.note = text
        self.verses = verses

    def insert(self):
        MongoDriver.get_client()["notes"]["all_notes"].insert_one(self.todict)

    def todict(self):
        self_dict = asdict(self)
        self_dict["verses"] = [verse.VERSE_TEXT for verse in self_dict["verses"]]
