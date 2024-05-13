import unittest
from unittest.mock import patch
from datetime import datetime
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
        note_split_level_1 = BibleNoteMD._split_notes(test_note, 0)

        self.assertEqual(note_split_level_1[0], h0)

        # Note - note split strips note.
        self.assertEqual(note_split_level_1[1], f"{h1}\n{h2}".strip())
        self.assertEqual(note_split_level_1[2], f"{h1}\n{h2_2}\n{h3}\n{h2}".strip())

        # Test level two splits.
        note_split_level_2 = BibleNoteMD._split_notes(note_split_level_1[1], 1)

        self.assertEqual(note_split_level_2[0], h1.strip())
        self.assertEqual(note_split_level_2[1], h2.strip())

        note_split_level_2 = BibleNoteMD._split_notes(note_split_level_1[2], 1)

        self.assertEqual(note_split_level_2[0], h1.strip())
        self.assertEqual(note_split_level_2[1], f"{h2_2}\n{h3}".strip())
        self.assertEqual(note_split_level_2[2], f"{h2}".strip())

        # Test level three splits
        note_split_level_3 = BibleNoteMD._split_notes(note_split_level_2[1], 2)

        self.assertEqual(note_split_level_3[0], h2_2.strip())
        self.assertEqual(note_split_level_3[1], h3.strip())

        note_split_level_3 = BibleNoteMD._split_notes(note_split_level_2[2], 2)

        self.assertEqual(note_split_level_3[0], h2.strip())
        self.assertTrue(len(note_split_level_3) == 1)

    def test_child_inheritence(self):

        # Set uup parent/child verses.
        parent_kv_tags = {"tagged": False, "existing_tag": "here"}
        parent_tags = {"one", "three"}
        parent_referenced_verses = {"/John/1/1", "/John/1/2"}

        bible_note_parent = BibleNoteMD(
            _id="_idabc",
            note_text="this is normal text.",
            theme="this is a . normal theme",
            key_value_tags=parent_kv_tags,
            tags=parent_tags,
            date_created=datetime.now(),
            date_updated=datetime.now(),
            referenced_verses=parent_referenced_verses,
        )

        child_id = "_id1234545"
        child_kv_tags = {"tagged": True, "new_tag": "is_here"}
        child_tags = {"one", "two"}
        child_referenced_notes = {"_id9108103"}
        child_referenced_verses = {"/John/1/1", "/John/1/2"}

        bible_note_child = BibleNoteMD(
            _id=child_id,
            note_text="asfj2093",
            theme="28032j",
            key_value_tags=child_kv_tags,
            tags=child_tags,
            date_created=datetime.now(),
            date_updated=datetime.now(),
            referenced_notes=child_referenced_notes,
            referenced_verses=child_referenced_verses,
        )

        # Copy objects to test for attributes which shouldn't change.
        bible_note_child_dict = bible_note_child.to_db_dict()
        parent_note_dict = bible_note_parent.to_db_dict()

        # Simulate updated values to test.
        updated_parent_kv_tags = parent_kv_tags
        for key, value in child_kv_tags.items():
            if key not in parent_kv_tags:
                updated_parent_kv_tags[key] = value

        updated_parent_tags = parent_tags.copy()
        updated_parent_tags.update(child_tags)

        updated_referenced_notes = child_referenced_notes.copy()
        updated_referenced_notes.add(child_id)

        updated_referenced_verses = child_referenced_verses

        # Inherit child in parent.
        bible_note_parent._inherit_child_note(bible_note_child)

        # Ensure parent inherited values are correct.
        self.assertEqual(bible_note_parent.key_value_tags, updated_parent_kv_tags)
        self.assertEqual(bible_note_parent.tags, updated_parent_tags)
        self.assertEqual(bible_note_parent.referenced_verses, updated_referenced_verses)
        self.assertEqual(bible_note_parent.referenced_notes, updated_referenced_notes)

        # Ensure child is unchanged.
        self.assertEqual(bible_note_child.to_db_dict(), bible_note_child_dict)

        # Ensure other parent values are unchanged.
        new_parent_dict = bible_note_parent.to_db_dict()
        del new_parent_dict["tags"]
        del new_parent_dict["key_value_tags"]
        del new_parent_dict["referenced_notes"]
        del new_parent_dict["referenced_verses"]
        del parent_note_dict["referenced_verses"]
        del parent_note_dict["referenced_notes"]
        del parent_note_dict["tags"]
        del parent_note_dict["key_value_tags"]
        self.assertEqual(new_parent_dict, parent_note_dict)

    @patch("bible_notes_md.BibleNoteMD.get")
    def test_set_self_from_db(self, mock_get_bible_note):
        # Create preliminary data required
        note_id = "12234509147018390"

        note_text = f"@_id{note_id}@\n" + test_note[:]

        note_in_mongo = BibleNoteMD(
            _id=note_id,
            note_text=note_text,
            referenced_notes={"1901830113", "910930909"},
            referenced_verses={"/John1/1/1", "/Genesis/1/1"},
            tags={"tagged"},
            key_value_tags={"tagged": True},
        )

        mock_get_bible_note.return_value = note_in_mongo

        note_in_mongo_dict = note_in_mongo.to_db_dict()

        parent_note = BibleNoteMD._split_notes(
            note_text=note_text, header_level_of_parent=0
        )[0]

        # Pass id, then remove it, to bypass extraction.
        new_bible_note = BibleNoteMD(_id="190190", note_text=note_text)
        new_bible_note._id = None

        # Set attritubes of new bible note.
        self.assertTrue(new_bible_note._set_self_from_db(parent_note))
        self.assertEqual(note_in_mongo_dict, new_bible_note.to_db_dict())

        # Test that self is not replaced if note text is different.
        # Pass id, then remove it, to bypass extraction.
        new_bible_note = BibleNoteMD(_id="190190", note_text=note_text + ".")
        new_bible_note._id = None

        self.assertFalse(new_bible_note._set_self_from_db(parent_note))
        self.assertNotEqual(note_in_mongo_dict, new_bible_note.to_db_dict())


if __name__ == "__main__":
    unittest.main()
