import re

from compiler_core import compile_post, BLOGPOST_MARKUP_REFERENCE, AUTHOR_MARKUP_REFERENCE, TAG_MARKUP_REFERENCE
from misc import read_file, write_file, done, nothing_to_do
from readable_queries import get_all_nodes
from sqlbase import BlogPost, db, Author, Tag

from sqlalchemy import desc
from sqlalchemy.sql.expression import func


def create_reference_table() -> dict:
    # Create a dict of the form "word" -> ("regex", "reference")
    # So for example for the blogpost "spirit" -> "\[.*?\]|(spirit)", "{{ blogpost: 13 }}"
    # The word is kept so that we can stop a page from referencing itself.
    word_regex_reference_triples = dict()
    node_sets = {
        AUTHOR_MARKUP_REFERENCE: db.query(Author).all(),
        TAG_MARKUP_REFERENCE: db.query(Tag).all(),

        # Apply longest term first: Prefer "world spirit" over "spirit".
        # Also last so blogposts tage precedence over author and tag names.
        BLOGPOST_MARKUP_REFERENCE: get_all_nodes().order_by(desc(func.length(BlogPost.name))),
    }

    for reference_type, nodes in node_sets.items():
        for node in nodes:
            regex_source = rf"\[.*?\]|({re.escape(node.name)})"
            regex = re.compile(regex_source, flags=re.IGNORECASE)
            word_regex_reference_triples[node.name] = (regex, reference_type.produce_reference(node.id))

    print(f"Generated {len(word_regex_reference_triples)} referencable terms.")
    return word_regex_reference_triples


def create_node_interstage(reference_table: dict, node: BlogPost) -> None:
    # The interstage is the user markdown with the
    # node references mixed in. This interstage is
    # what will then be turned into html.

    markdown = read_file(node.markdown_path)
    for word, (regex, reference) in reference_table.items():
        # ...stop a page from referencing itself.
        if word == node.name:
            continue

        # Turn word into syntax [word]({{ post: X }}).
        # We have to do some lambda magic to avoid silly overlapping issues.
        markdown = regex.sub(
            lambda match: rf"[{match.group(1)}]({reference})" if match.group(1) else match.group(0),
            markdown)

    write_file(node.interstage_path, markdown)


def compile_all_graph_pages() -> None:
    print("Compiling graph pages...")
    if nodes := get_all_nodes().all():
        reference_table = create_reference_table()
        for node in nodes:
            print(f"Compiling graph page \"{node.name}\"... ", end="", flush=True)
            create_node_interstage(reference_table, node)
            compile_post(node)
            done()
        done()

    else:
        nothing_to_do()
