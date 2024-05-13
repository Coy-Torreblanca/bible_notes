# https://bible-notes.atlassian.net/wiki/spaces/~63cdc33695cff7f585c2a3dd/pages/33861/BNMD

import re
from typing import Optional
from bible_notes import BibleNote
from dataclasses import dataclass, field


@dataclass
class BibleNoteMD(BibleNote):

    header_level: int = 0

    def __post_init__(self):
        super().__post_init__()

        if not self._id:
            self.extract()

    def extract(self) -> None:
        """Extract object attributes from note_text."""

        # Split parent from child notes.
        split_notes = self.note_text.split("#" * self.header_level + " @ ")
        parent_note = split_notes[0]

        # Check if note is in Mongo database and this note hasn't been updated.
        if self._set_self_from_db(parent_note):
            return

        children_notes = self._split_notes[1:]

        # Inherit from child note ids in parent.
        child_ids_in_parent = re.findall("^@__id([a-z0-9]+)@$", parent_note, flags=re.M)
        for child_id in child_ids_in_parent:
            child_note = BibleNote.get(_id=child_id)
            self._inherit_child_note(child_note=child_note)

        # Add child note ids to parent_note.
        child_ids_in_parent[0] = "\n" + child_ids_in_parent
        parent_note += "\n".join(child_ids_in_parent)

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

    def _set_self_from_db(self, parent_note_text: str) -> bool:
        """Set attributes from mongodb if text matches note in mongodb.

        Args:
            parent_note_text (str): The note of most parent text without child note text.


        Returns:
            bool: Whether self attributes could be set from mongodb.
        """

        if not self._id:
            _id = re.search("^@_id([a-z0-9]+)@$", parent_note_text, flags=re.M)

            bible_note = BibleNoteMD.get(_id=_id)

            # Set this object equal to the object in the database for simplicity.
            if bible_note.note_text == self.note_text:
                for attribute, value in bible_note.to_db_dict().items():
                    self.__setattr__(attribute, value)
                return True

            return False

    def _inherit_child_note(self, child_note: "BibleNoteMD") -> None:
        """Inherit attributes from the provided child note to this object.
        NOTE - Does not modify self.note_text.

        Args:
            child_note (BibleNoteMD): Child note to inherit from.
        """
        # Add child tags to parent.
        for key, value in child_note.key_value_tags.items():
            if key not in self.tags:
                self.key_value_tags[key] = value

        self.tags.update(child_note.tags)

        # Add child verse/note references to parent.
        self.referenced_verses.update(child_note.referenced_verses)
        self.referenced_notes.update(child_note.referenced_notes)
        self.referenced_notes.add(child_note._id)
