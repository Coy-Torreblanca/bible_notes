# https://bible-notes.atlassian.net/wiki/spaces/~63cdc33695cff7f585c2a3dd/pages/33861/BNMD

import re
import uuid
from typing import Optional
from bible_notes import BibleNote
from dataclasses import dataclass, field

CHILD_ID_REGEX = "^@__id([a-z0-9]+)@$"
_ID_REGEX = "^@_id([a-z0-9]+)@$"
TAGS_REGEX = "^@tags\n^([\s\S]+)\n^@$"
VERSE_REGEX = "@(\/.*)@"
THEME_REGEX = "^@theme$\n^([\s\S]+?)^@$"
TITLE_REGEX = "^{additional_level_hashtags} @ (.*)$"


@dataclass
class BibleNoteMD(BibleNote):

    header_level: int = 0

    def __post_init__(self):
        super().__post_init__()

        self.note_text = self.note_text.strip()

        # If note starts with a header, then set starting header_level to 1.
        if self.note_text.startswith("# @ "):
            self.header_level = 1

        if not self._id:
            self.extract()

    def extract(self) -> None:
        """Extract object attributes from note_text."""

        # Split parent from child notes.
        split_notes = self._split_notes(self.note_text, self.header_level)
        parent_text = split_notes[0]

        self._extract_attr_from_parent_text(parent_text=parent_text)

        children_notes = self._split_notes[1:]

        # if not _id:
        # raise ValueError("Note text did not contain a valid _id field.")

    @classmethod
    def _split_notes(cls, note_text: str, header_level_of_parent: int) -> list[str]:
        """Split notes into a list containing text of parent note and immediate sub-notes.

        Args:
            note_text (str): The text to split be headers.
            header_level_of_parent (int): The header level of the parent.

        Returns:
            list[str]: A list containing text of parent note and immediate sub-notes.
        """

        header_of_immediate_child_notes = "#" * (header_level_of_parent + 1) + " @ "
        split_notes = re.split(rf"\n{header_of_immediate_child_notes}", note_text)

        # Add headers back and strip.
        split_notes[0] = split_notes[0].strip()
        for i in range(1, len(split_notes)):
            split_notes[i] = (
                f"{ header_of_immediate_child_notes }{ split_notes[i].strip() }"
            )

        return split_notes

    def _extract_attr_from_parent_text(self, parent_text: str) -> None:
        """Extract attributes from parent text, including child_ids in parent text..
        attributes: tags, referenced_verses, referenced_notes.

        Args:
            parent_text (str): Text of note without child note text.
        """
        # Extract/Create _id.
        if not self._id:
            _id = re.search(_ID_REGEX, parent_text, flags=re.M)

            _id = uuid.uuid4() if not _id else _id.group(1)

            self._id = _id

        # If note is in db and not modified, set attributes from db.
        if self._set_self_from_db():
            return

        # Extract tags.
        self._process_tag_text(parent_text=parent_text)

        # Extract verse_references.
        self.referenced_verses = set(re.findall(VERSE_REGEX, parent_text, re.M))

        # Extract theme.
        match = re.search(THEME_REGEX, parent_text, re.M)
        self.theme = match if not match else match.group(1).strip()

        # Extract Title.
        if not self.title and self.header_level > 0:
            # If title is not the filename, extract it from next header.
            match = re.search(
                TITLE_REGEX.format("#" * self.header_level), parent_text, re.M
            )

            if match:
                self.title = match.group(1)

        # Extract attributes from child_ids.

    def _process_tag_text(self, parent_text: str) -> None:
        """Test tag text into kv and regular tags.

        Args:
            parent_text (str): Text of note without child note text.
            Tags are extract from the following format in parent_text:

            @tags
            tag_key 1: tag_value 1
            tag 2
            @
        """

        # Extract tags.
        match = re.search(TAGS_REGEX, parent_text, re.M)
        if not match:
            return

        for tag in match.group(1).split("\n"):
            # Split tag and check if kv tag.
            split_tag = tag.split(":")

            if len(split_tag) == 1:
                # This is a regular tag.
                self.tags.add(split_tag[0])
                continue

            if split_tag[1]:
                # This is a kv tag.
                self.key_value_tags[split_tag[0]] = split_tag[1]

            else:
                # This is a kv tag with a null key.
                self.tags.add(split_tag[0])

    def _set_self_from_db(self) -> bool:
        """Set attributes from mongodb if text matches note in mongodb.
        Extract and set _id field.

        Returns:
            bool: Whether self attributes could be set from mongodb.
        """

        assert self._id

        bible_note = BibleNoteMD.get(_id=self._id)

        # Set this object equal to the object in the database for simplicity.
        if bible_note.note_text == self.note_text:
            for attribute, value in bible_note.to_db_dict().items():
                self.__setattr__(attribute, value)
            return True

        return False

    def _process_child_ids_in_parent_text(self, parent_text: str) -> None:
        """Retrieve child ids from parent note.
        Inherit child notes.

        Args:
            parent_text (str): Text of parent note wihout child note text.
        """

        # Inherit from child note ids in parent.
        child_ids_in_parent = re.findall(CHILD_ID_REGEX, parent_text, flags=re.M)
        for child_id in child_ids_in_parent:
            child_note = BibleNote.get(_id=child_id)
            if child_note:
                self._inherit_child_note(child_note=child_note)

    def _inherit_child_note(self, child_note: "BibleNoteMD") -> None:
        """Inherit attributes from the provided child note to this object.
        NOTE - Does not modify self.note_text.

        Args:
            child_note (BibleNoteMD): Child note to inherit from.
        """
        # Add child tags to parent.
        if child_note.key_value_tags:
            for key, value in child_note.key_value_tags.items():
                if key not in self.tags:
                    self.key_value_tags[key] = value

            self.tags.update(child_note.tags)

        # Add child verse/note references to parent.
        self.referenced_verses.update(child_note.referenced_verses)
        self.referenced_notes.update(child_note.referenced_notes)
        self.referenced_notes.add(child_note._id)
