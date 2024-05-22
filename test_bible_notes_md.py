import unittest
import re
from unittest.mock import patch
from datetime import datetime
from bible_notes_md import (
    BibleNoteMD,
    CHILD_ID_REGEX,
    TAGS_REGEX,
    _ID_REGEX,
    VERSE_REGEX,
)

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
tag_key2:
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

        # Create mock function which will only except target id and return mongo note.

        def mock_function_side_affect(_id):
            if _id == note_id:
                return note_in_mongo

            else:
                self.fail(f"Provided argument was not expected id: {_id}")

        mock_get_bible_note.side_effect = mock_function_side_affect

        note_in_mongo_dict = note_in_mongo.to_db_dict()

        new_bible_note = BibleNoteMD(_id=note_id, note_text=note_text)

        # Set attritubes of new bible note.
        self.assertTrue(new_bible_note._set_self_from_db())
        self.assertEqual(note_in_mongo_dict, new_bible_note.to_db_dict())

        # Test that self is not replaced if note text is different.
        # Pass id, then remove it, to bypass extraction.
        new_bible_note = BibleNoteMD(_id=note_id, note_text=note_text + ".")

        self.assertFalse(new_bible_note._set_self_from_db())
        self.assertNotEqual(note_in_mongo_dict, new_bible_note.to_db_dict())

    @patch("bible_notes_md.BibleNote.get")
    def test_process_child_ids_in_parent(self, bible_note_md_get):

        child_id = "13902943"
        child_kv_tags = {"tagged": True}
        child_tags = {"tagged"}
        child_bible_note = BibleNoteMD(
            _id=child_id, note_text=h2, key_value_tags=child_kv_tags, tags=child_tags
        )

        child_id_2 = "8503708asjk"
        child_kv_tags_2 = {"not_tag": True}
        child_tags_2 = {"tagged"}
        child_bible_note_2 = BibleNoteMD(
            _id=child_id_2,
            note_text=h2_2,
            key_value_tags=child_kv_tags_2,
            tags=child_tags_2,
        )

        def mock_function(_id):
            if _id == child_id:
                return child_bible_note
            elif _id == child_id_2:
                return child_bible_note_2

            self.fail(
                f"Incorrect argument provided: {_id}. expected: {child_id} or {child_id_2}"
            )

        bible_note_md_get.side_effect = mock_function

        parent_text = (
            h1
            + "\n"
            + f"@__id{child_id}@"
            + "\n"
            + f"@__id{child_id_2}@"
            + "\n@_id1903910193910@"
        )

        parent_note = BibleNoteMD(
            _id="id1903910193910", note_text=parent_text, header_level=1
        )

        split_notes = parent_note._split_notes(
            parent_note.note_text, parent_note.header_level
        )

        parent_note._process_child_ids_in_parent_text(split_notes[0])

        self.assertEqual(parent_note.referenced_notes, {child_id, child_id_2})

        self.assertEqual(
            parent_note.key_value_tags, {**child_kv_tags, **child_kv_tags_2}
        )

        self.assertEqual(parent_note.tags, child_tags | child_tags_2)

    def _test_process_tags(self):

        bible_note = BibleNoteMD(_id="1234")

        bible_note._process_tag_text(h0)

        self.assertEqual(bible_note.key_value_tags, {"tag_key 1": "tag_value 1"})
        self.assertEqual(bible_note.tags, {"tag2", "tag3", "tag4"})


class TestBibleNoteMDRegexes(unittest.TestCase):
    def test_CHILD_ID_REGEX(self):
        child_ids = ["@__id123402990@", "@__id18301910@", "@__id9109909209ajslkdfj@"]

        h0_w_child_ids = h0 + "\n@_id120919@\n" + "\n".join(child_ids)
        h1_w_child_ids = h1 + "\n@_id9010asdfa0@\n" + "\n".join(child_ids)

        # remove @__id and @ from child ids.
        child_ids = [
            child_id.replace("__id", "").replace("@", "") for child_id in child_ids
        ]

        child_ids_h0 = re.findall(CHILD_ID_REGEX, h0_w_child_ids, flags=re.M)

        self.assertEqual(child_ids_h0, child_ids)

        child_ids_h1 = re.findall(CHILD_ID_REGEX, h1_w_child_ids, flags=re.M)

        self.assertEqual(child_ids_h1, child_ids)

    def test_ID_REGEX(self):
        _ids = ["@_id123402990@", "@_id18301910@", "@_id9109909209ajslkdfj@"]

        h0_w_ids = h0 + "\n" + "\n".join(_ids)
        h1_w_ids = h1 + "\n" + "\n".join(_ids)

        # remove @_id and @ from child ids.
        _ids = [_id.replace("_id", "").replace("@", "") for _id in _ids]

        _ids_h0 = re.findall(_ID_REGEX, h0_w_ids, flags=re.M)

        self.assertEqual(_ids_h0, _ids)

        _ids_h1 = re.findall(_ID_REGEX, h1_w_ids, flags=re.M)

        self.assertEqual(_ids_h1, _ids)

    def test_header_regex(self):

        # Level 0
        header_level = 0
        next_header_regex = "\n" + "#" * (header_level + 1) + " @ "

        match = re.search(next_header_regex, h0 + "\n" + h1)

        self.assertIsNotNone(match)

        self.assertEqual(match.group(0), "\n# @ ")

        # Level 1
        header_level = 1

        next_header_regex = "\n" + "#" * (header_level + 1) + " @ "

        match = re.search(next_header_regex, h1 + "\n" + h2)

        self.assertIsNotNone(match)

        self.assertEqual(match.group(0), "\n## @ ")

    def test_TAGS_REGEX(self):

        expected_output = """tag_key 1: tag_value 1\ntag 2\ntag 3\ntag 4\ntag_key2:"""

        match = re.search(TAGS_REGEX, h0, re.M)

        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), expected_output)


if __name__ == "__main__":
    unittest.main()
