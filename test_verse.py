import unittest
from verse import *


class TestVerse(unittest.TestCase):
    def test_creation(self):
        self.assertEqual(
            Verse(
                BOOK="John",
                CHAPTER_NUMBER=1,
                VERSE_NUMBER=1,
            ).VERSE_TEXT,
            "In the beginning was the Word, and the Word was with God, and the Word was God.",
        )

    def test_creation_id(self):
        self.assertEqual(
            Verse(_id="kjv/John/1/1").VERSE_TEXT,
            Verse(
                BOOK="John",
                CHAPTER_NUMBER=1,
                VERSE_NUMBER=1,
            ).VERSE_TEXT,
        )


if __name__ == "__main__":
    unittest.main()
