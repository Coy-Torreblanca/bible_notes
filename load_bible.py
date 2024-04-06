import pymongo
import json
import os
from db.driver import MongoDriver
from verse import Verse

# TODO use unified scripture xlm
# https://ubsicap.github.io/usx/vocabularies.html


def insert_bible(translation: str):
    with open(
        "/Users/coytorreblanca/Documents/bible/data/bible_databases/json/key_english.json"
    ) as f:
        keys = json.load(f)["resultset"]["keys"]
        num_book_map = {}

        for key in keys:
            num_book_map[key["b"]] = key["n"]

    with open(
        f"/Users/coytorreblanca/Documents/bible/data/bible_databases/json/t_{translation}.json"
    ) as f:
        bible = json.load(f)["resultset"]["row"]

        for verse in bible:
            verse = verse["field"]

            book = num_book_map[verse[1]]
            chapter_number = verse[2]
            verse_number = verse[3]
            verse_text = verse[4]

            verse = Verse(
                BOOK=book,
                CHAPTER_NUMBER=chapter_number,
                VERSE_NUMBER=verse_number,
                VERSE_TEXT=verse_text,
                TRANSLATION=translation,
            )

            # translation is database
            # book is collection
            MongoDriver.get_client()[translation][book].insert_one(verse.todict())


ABRV_BOOK_MAP = {
    "1CH": "1 Chronicles",
    "1CO": "1 Corinthians",
    "1JO": "1 John",
    "1KI": "1 Kings",
    "1PE": "1 Peter",
    "1SA": "1 Samuel",
    "1TH": "1 Thessalonians",
    "1TI": "1 Timothy",
    "2CH": "2 Chronicles",
    "2CO": "2 Corinthians",
    "2JO": "2 John",
    "2KI": "2 Kings",
    "2PE": "2 Peter",
    "2SA": "2 Samuel",
    "2TH": "2 Thessalonians",
    "2TI": "2 Timothy",
    "3JO": "3 John",
    "ACT": "Acts",
    "AMO": "Amos",
    "COL": "Colossians",
    "DAN": "Daniel",
    "DEU": "Deuteronomy",
    "ECC": "Ecclesiastes",
    "EPH": "Ephesians",
    "EST": "Esther",
    "EXO": "Exodus",
    "EZE": "Ezekiel",
    "EZR": "Ezra",
    "GAL": "Galatians",
    "GEN": "Genesis",
    "HAB": "Habakkuk",
    "HAG": "Haggai",
    "HEB": "Hebrews",
    "HOS": "Hosea",
    "ISA": "Isaiah",
    "JAM": "James",
    "JER": "Jeremiah",
    "JOB": "Job",
    "JOE": "Joel",
    "JOH": "John",
    "JON": "Jonah",
    "JOS": "Joshua",
    "JDG": "Judges",
    "JDE": "Jude",
    "LAM": "Lamentations",
    "LEV": "Leviticus",
    "LUK": "Luke",
    "MAL": "Malachi",
    "MAR": "Mark",
    "MAT": "Matthew",
    "MIC": "Micah",
    "NAH": "Nahum",
    "NEH": "Nehemiah",
    "NUM": "Numbers",
    "OBA": "Obadiah",
    "PRO": "Proverbs",
    "PSA": "Psalms",
    "REV": "Revelation",
    "ROM": "Romans",
    "RUT": "Ruth",
    "SOS": "Song of Solomon",
    "TIT": "Titus",
    "ZEC": "Zechariah",
    "ZEP": "Zephaniah",
    "PHP": "Philippians",
    "PHM": "Philemon",
}


def insert_references():
    client = MongoDriver.get_client()

    for filename in os.listdir(
        "/Users/coytorreblanca/Documents/bible/data/bible-cross-reference-json"
    ):
        if not filename.endswith(".json"):
            continue

        file = json.load(
            open(
                os.path.join(
                    "/Users/coytorreblanca/Documents/bible/data/bible-cross-reference-json",
                    filename,
                )
            )
        )

        for reference in file.values():
            _reference = {}
            verse = reference["v"]

            book, cn, vn = verse.split(" ")
            book = ABRV_BOOK_MAP[book]

            _id = f"{book}/{cn}/{vn}"
            _reference["verse"] = _id
            _reference["_id"] = _id
            _reference["references"] = []

            verse_book = book

            if "r" in reference:
                for verse in reference["r"].values():
                    book, cn, vn = verse.split(" ")
                    book = ABRV_BOOK_MAP[book]

                    _id = f"{book}/{cn}/{vn}"
                    _reference["references"].append(_id)

            try:
                client["references"][verse_book].insert_one(_reference)

            except pymongo.errors.DuplicateKeyError:
                pass


if __name__ == "__main__":
    # insert_references()
    insert_bible("asv")
