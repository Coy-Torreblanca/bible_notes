# https://bible-notes.atlassian.net/wiki/spaces/~63cdc33695cff7f585c2a3dd/pages/33861/BNMD

import re
from db.driver import MongoDriver
from bible_notes import BibleNote
from dataclasses import dataclass
from typing import Optional

REFERENCE_NOTE_ID_REGEX = "^@__id(.+)@$"
_ID_REGEX = "^@_id(.+)@$"
TAGS_REGEX = "^@tags\n^([\s\S]+)\n^@$"
VERSE_REGEX = "@(\/.*)@"
THEME_REGEX = "^@theme$\n^([\s\S]+?)^@$"
TITLE_REGEX = "^{additional_level_hashtags} @ (.*)$"


@dataclass
class BibleNoteMD(BibleNote):

    header_level: int = 0

    MONGO_DATABASE = "notes_md"
    MONGO_COLLECTION = "all_notes_md"

    def __post_init__(self):

        assert self.note_text
        self.note_text = self.note_text.strip()

        self.note_text = self._normalize_text_headers(self.note_text)

        # If note starts with a header, then set starting header_level to 1.
        if self.note_text.startswith("# @ "):
            self.header_level = 1

    def extract(self) -> None:
        """Extract object attributes from note_text."""

        self.child_notes = self._contract_note()
        self._extract_attr_from_parent_text(self.note_text)

        assert self._id

        # Add parent_id to child notes.
        for child_note in self.child_notes:
            child_note.parent_ids.add(self._id)
            child_note.extract()

        # Get parent ids from database if present.
        existing_parent_ids = MongoDriver.get_client()[self.MONGO_DATABASE][
            self.MONGO_COLLECTION
        ].find_one({"_id": self._id}, {"parent_ids": 1, "_id": 0})

        if existing_parent_ids:
            self.parent_ids.update(existing_parent_ids["parent_ids"])

    @classmethod
    def get(cls, _id: str) -> Optional["BibleNoteMD"]:
        """From the database, get the object represented by the given note_id.

        Returns:
            Note or None: Return None if there is no data related to the note_id provided.
                          Otherwise, provide the given Note object associated with the note_id.
        """
        return super().get(_id)

    @classmethod
    def _normalize_text_headers(cls, note_text: str) -> str:
        """_Make first header of note text and shift all other headings by the same amount

        Args:
            note_text (str): Note text to normalize

        Returns:
            str: normalized note text
        """

        first_header = re.search("^(#+).*$", note_text, re.M)

        if not first_header:
            return note_text

        header_length = len(first_header.group(1))

        return cls._subtract_header_levels(header_length - 1, note_text)

    @classmethod
    def _subtract_header_levels(cls, number_to_subtract: int, text: str) -> str:
        """Remove the requested number of header levels from all headers in text.
        I.E. to remove a single level from: `## @ level_one` will result in `# @ level one`
        WARN: Undefined results if number_to_subtract is greater than the smallest header in text.

        Args:
            number_to_subtract (int): Number of levels to remove from all headers in text.
            text (str): Text from which to remove header levels from.

        Returns:
            str: Text with reduced headers.
        """

        return re.sub(
            f"^#{{{number_to_subtract}}}(#*.*$)",
            "\g<1>",
            text,
            flags=re.M,
        )

    @classmethod
    def _add_header_levels(cls, number_to_add: int, text: str) -> str:
        """Add the requested number of header levels from all headers in text.
        I.E. to add a single level to: `## @ level_one` will result in `### @ level one`

        Args:
            number_to_add (int): Number of levels to add to all headers in text.
            text (str): Text from which to add header levels to.

        Returns:
            str: Text with added headers.
        """

        return re.sub(
            f"^#+.*$",
            f"{'#' * number_to_add}\g<0>",
            text,
            flags=re.M,
        )

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
                f"{ header_of_immediate_child_notes}{ split_notes[i].strip() }"
            )

        return split_notes

    def _contract_note(self) -> list["BibleNoteMD"]:
        """Extract child note ids from note text and remove child notes from note text.
        Return immediate child objects.

        Returns:
            list[BibleNoteMD]: Returns child notes (immediate children).
        """

        self.child_ids = []
        split_notes = self._split_notes(self.note_text, self.header_level)

        self.note_text = split_notes[0]

        child_notes = []
        for i in range(1, len(split_notes)):
            note = split_notes[i]
            note = BibleNoteMD(note_text=self._normalize_text_headers(note))
            child_notes.append(note)
            self.child_ids.append(note._id)

        return child_notes

    def _expand_note(self) -> None:
        """Add unormalized child notes to parent note text."""

        child_texts = []

        new_referenced_notes = []

        for child_id in self.referenced_notes:
            child_note = BibleNoteMD.get(child_id)

            if child_note:
                new_referenced_notes.append(child_id)

            else:
                continue

            if self.header_level:
                child_texts.append(
                    child_note._add_header_levels(
                        self.header_level, child_note.note_text
                    )
                )

            else:
                child_texts.append(child_note.note_text)

        # Remove deleted child notes.
        self.referenced_notes = new_referenced_notes

        return "{parent_text}\n{child_notes}".format(
            parent_text=self.note_text, child_notes="\n".join(child_texts)
        )

    def _extract_attr_from_parent_text(self, parent_text: str) -> None:
        """Extract attributes from parent text parent text..
        attributes: tags, referenced_verses, referenced_notes.

        Args:
            parent_text (str): Text of note without child note text.
        """

        # Extract tags.
        self._process_tag_text(parent_text=parent_text)

        # Extract referenced_verses.
        self.referenced_verses = set(re.findall(VERSE_REGEX, parent_text, re.M))

        # Extract referenced_notes.
        self.referenced_notes = self._process_note_references_in_parent_text(
            parent_text=parent_text
        )

        # Extract theme.
        match = re.search(THEME_REGEX, parent_text, re.M)
        self.theme = match if not match else match.group(1).strip()

        # Extract Title.
        if self.header_level > 0:
            # If title is not the filename, extract it from next header.
            match = re.search(
                TITLE_REGEX.format(additional_level_hashtags="#" * self.header_level),
                parent_text,
                re.M,
            )

            assert match

            self.title = match.group(1)

        # Extract id.
        self._extract_id(parent_text)

    def _process_tag_text(self, parent_text: str) -> None:
        """Extract tag text into kv and regular tags.

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
                self.key_value_tags[split_tag[0].strip()] = split_tag[1].strip()

            else:
                # This is a kv tag with a null key.
                self.tags.add(split_tag[0])

    def _extract_id(self, parent_text: str) -> None:
        """Extract (or generate) parent id from text.
        self.title is required to generate a heading 1+ id.

        Args:
            parent_text (str): Text of note without child note text.
            _id is in format @_id.*@.
        """
        if self._id:
            return

        # Extract id.
        match = re.search(_ID_REGEX, parent_text, flags=re.M)

        if match:
            self._id = match.group(1)
            return

        self._id = BibleNoteMD._generate_new_id()

        # Add id to note.
        if self.header_level == 0:
            self.note_text = f"@_id{self._id}@" + "\n" + self.note_text
            return

        assert self.title

        self.note_text = self.note_text.replace(
            self.title, self.title + "\n" + f"@_id{self._id}@" + "\n"
        )

    def set_self_from_db(self, check_note_text: bool = False) -> bool:
        """Set attributes from mongodb if text matches note in mongodb.
        Extract and set _id field.

        NOTE: Assumes self has been contracted.

        Returns:
            bool: Whether self attributes could be set from mongodb.
        """

        assert self._id

        bible_note = BibleNoteMD.get(_id=self._id)

        # Set this object equal to the object in the database for simplicity.
        if not bible_note:
            # Note not found in database.
            return False

        bible_note._expand_note()

        if check_note_text and self.note_text != bible_note.note_text:
            # Note found in database, but note_text does not match.
            return False

        for attribute, value in bible_note.to_db_dict().items():
            self.__setattr__(attribute, value)

        return True

    def _process_note_references_in_parent_text(self, parent_text: str) -> list[str]:
        """Retrieve child ids from parent note.
        Inherit child notes.

        Args:
            parent_text (str): Text of parent note wihout child note text.
        """

        referenced_notes = []
        # Inherit from child note ids in parent.
        for reference in re.findall(REFERENCE_NOTE_ID_REGEX, parent_text, flags=re.M):
            referenced_notes.append(reference)
        return referenced_notes

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
        for child_id in child_note.referenced_notes:
            self.referenced_notes.append(child_id)
