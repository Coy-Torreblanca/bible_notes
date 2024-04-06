import re
from verse import Verse
from notes import Note
import argparse


def get_verse(args):
    # TODO books starting with a number are not being captilized.
    book = args.book.capitalize() if not re.search("^\d", args.book) else args.book

    verse = Verse(
        BOOK=book, CHAPTER_NUMBER=args.chapter_number, VERSE_NUMBER=args.verse_number
    )

    if args.do_not_get_reference_text:
        verse.get_reference_texts()

    print(verse.__str__())


def main():
    parser = argparse.ArgumentParser(description="Bible Notes")
    subparser = parser.add_subparsers(title="subcommands", dest="subcommand")

    # parse for get verse
    get_verse_parser = subparser.add_parser(
        "get_verse", help="Get a bible verse", aliases=["v"]
    )

    get_verse_parser.add_argument("book", type=str, help="Book of the bible.")
    get_verse_parser.add_argument(
        "chapter_number", type=int, help="Chapter of target verse."
    )
    get_verse_parser.add_argument("verse_number", type=str, help="Verse number.")
    get_verse_parser.add_argument(
        "--do_not_get_reference_text",
        "-nr",
        action="store_false",
        help="Whether to get verse text of references.",
        default=True,
    )
    get_verse_parser.set_defaults(func=get_verse)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
