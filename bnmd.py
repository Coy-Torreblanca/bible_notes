# CLI BNMD

import click
from bible_notes_md import BibleNoteMD


@click.group()
def cli():
    pass


@click.command()
@click.argument("file", type=click.File("r"))
def write(file):
    lines = file.read()
    note = BibleNoteMD(note_text=lines)
    print(f"writing... {note.note_text}")


@click.command()
@click.argument("note_title", type=click.Choice())
def read():
    print("reading...")


cli.add_command(write)
cli.add_command(read)

if __name__ == "__main__":
    cli()
