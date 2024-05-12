import unittest
from bible_notes_md import BibleNoteMD

h0 = """asdlkfja;sdf

@theme
these is the theme text
there is two lines
@

@tags
tag_key 1: tag_value 1
tag 2
tag 3
tag 4
@"""

h1 = """
# @ Note One Title

@theme
these is the theme text
there is two lines
@

@tags
tag_key 1: tag_value 1
tag 2
tag 3
tag 4
@

@/asv/John/1/1-10@

I am referencing a bible verse; therefore, this entire note can be found
when searching for this verse.

"""

h2 = """
## @ Child Note Title (Note Two)
@_id1231291019@

@theme
...
@

@tags
...
@

This is an existing note; therefore, it will be updated with any new text I put in 
here."""

h2_2 = """
## @ Child Note Title (Note Three)
The _id field was added when I created this file from the parent note.


@theme
...
@

@tags
...
@

There is no _id field; therefore, this is a new note which will be created
when I upsert this text file.
"""

h3 = """
### @ Child Child Note Title (Note Three)
@_id12312910a290219@

@theme
...
@

@tags
...
@

This is an existing note; therefore, it will be updated with any new text I put in 
Hi hi hi.
"""

h2 = """
## @ Child Note Title (Note Two)
@_id1231291019@

@theme
...
@

@tags
...
@

This is an existing note; therefore, it will be updated with any new text I put in 
here."""

test_note = f"{h0}\n{h1}\n{h2}\n{h1}\n{h2_2}\n{h3}\n{h2}"


class TestBibleNotesMD(unittest.TestCase):
    def test_note_split(self):
        # Test level one split.
        note_split_level_1 = BibleNoteMD.split_notes(test_note, 0)

        self.assertEqual(note_split_level_1[0], h0)

        # Note - note split strips note.
        self.assertEqual(note_split_level_1[1], f"{h1}\n{h2}".strip())
        self.assertEqual(note_split_level_1[2], f"{h1}\n{h2_2}\n{h3}\n{h2}".strip())

        # Test level two splits.
        note_split_level_2 = BibleNoteMD.split_notes(note_split_level_1[1], 1)

        self.assertEqual(note_split_level_2[0], h1.strip())
        self.assertEqual(note_split_level_2[1], h2.strip())

        note_split_level_2 = BibleNoteMD.split_notes(note_split_level_1[2], 1)

        self.assertEqual(note_split_level_2[0], h1.strip())
        self.assertEqual(note_split_level_2[1], f"{h2_2}\n{h3}".strip())
        self.assertEqual(note_split_level_2[2], f"{h2}".strip())

        # Test level three splits
        note_split_level_3 = BibleNoteMD.split_notes(note_split_level_2[1], 2)

        self.assertEqual(note_split_level_3[0], h2_2.strip())
        self.assertEqual(note_split_level_3[1], h3.strip())

        note_split_level_3 = BibleNoteMD.split_notes(note_split_level_2[2], 2)

        self.assertEqual(note_split_level_3[0], h2.strip())
        self.assertTrue(len(note_split_level_3) == 1)


if __name__ == "__main__":
    unittest.main()
