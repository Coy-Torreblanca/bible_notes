# CLI BNMD
import re
import argparse
from bible_notes_md import BibleNoteMD


def write_note(args):
    note = BibleNoteMD(note_text="\n".join(args.note_path.readlines()))

    note.extract()


def main():
    parser = argparse.ArgumentParser(description="Bible Notes Mark Down")

    subparser = parser.add_subparsers(title="subcommands", dest="subcommand")

    # parser for writing bible notes.
    write_parser = subparser.add_parser(
        "write_note", help="Insert or update a note in the databases", aliases=["w"]
    )

    write_parser.add_argument("note_path", type=argparse.FileType(mode="r"))

    write_parser.set_defaults(func=write_note)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
