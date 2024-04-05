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

    def test_references(self):
        references = [
            "kjv/Exodus/20/11",
            "kjv/Exodus/31/18",
            "kjv/2 Kings/19/15",
            "kjv/1 Chronicles/16/26",
            "kjv/2 Chronicles/2/11",
            "kjv/Nehemiah/9/6",
            "kjv/Job/26/13",
            "kjv/Job/38/4",
            "kjv/Psalms/8/3",
            "kjv/Psalms/8/4",
            "kjv/Psalms/33/6",
            "kjv/Psalms/33/9",
            "kjv/Psalms/89/11",
            "kjv/Psalms/90/2",
            "kjv/Psalms/96/5",
            "kjv/Psalms/102/25",
            "kjv/Psalms/104/24",
            "kjv/Psalms/104/30",
            "kjv/Psalms/115/15",
            "kjv/Psalms/121/2",
            "kjv/Psalms/124/8",
            "kjv/Psalms/134/3",
            "kjv/Psalms/136/5",
            "kjv/Psalms/146/6",
            "kjv/Psalms/148/4",
            "kjv/Proverbs/3/19",
            "kjv/Proverbs/8/22",
            "kjv/Proverbs/16/4",
            "kjv/Ecclesiastes/12/1",
            "kjv/Isaiah/37/16",
            "kjv/Isaiah/40/26",
            "kjv/Isaiah/40/28",
            "kjv/Isaiah/42/5",
            "kjv/Isaiah/44/24",
            "kjv/Isaiah/45/18",
            "kjv/Isaiah/51/13",
            "kjv/Isaiah/51/16",
            "kjv/Isaiah/65/17",
            "kjv/Jeremiah/10/12",
            "kjv/Jeremiah/32/17",
            "kjv/Jeremiah/51/15",
            "kjv/Zechariah/12/1",
            "kjv/Matthew/11/25",
            "kjv/Mark/13/19",
            "kjv/John/1/1",
            "kjv/Acts/4/24",
            "kjv/Acts/14/15",
            "kjv/Acts/17/24",
            "kjv/Romans/1/19",
            "kjv/Romans/11/36",
            "kjv/1 Corinthians/8/6",
            "kjv/Ephesians/3/9",
            "kjv/Colossians/1/16",
            "kjv/Hebrews/1/2",
            "kjv/Hebrews/1/10",
            "kjv/Hebrews/3/4",
            "kjv/Hebrews/11/3",
            "kjv/2 Peter/3/5",
            "kjv/1 John/1/1",
            "kjv/Revelation/3/14",
            "kjv/Revelation/4/11",
            "kjv/Revelation/10/6",
            "kjv/Revelation/14/7",
            "kjv/Revelation/21/6",
            "kjv/Revelation/22/13",
        ]

        self.assertEqual(Verse(_id="kjv/Genesis/1/1").REFERENCES, references)


if __name__ == "__main__":
    unittest.main()
