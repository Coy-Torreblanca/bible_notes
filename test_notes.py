import unittest
from notes import Note
from verse import Verse


class TestNotes(unittest.TestCase):
    def test_verse_parse(self):
        text = """calsdjf dajfdlsf dasjsfl @John/1/1
fjasdfk @John/1/3 djasd"""

        note = Note(note=text)

        note_verse, test_verse = note.verses[0], Verse(
            BOOK="John", CHAPTER_NUMBER=1, VERSE_NUMBER=1
        )

        self.assertEqual(note_verse, test_verse)

        self.assertEqual(
            note.verses[1], Verse(BOOK="John", CHAPTER_NUMBER=1, VERSE_NUMBER=3)
        )


if __name__ == "__main__":
    unittest.main()
