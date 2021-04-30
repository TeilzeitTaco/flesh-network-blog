import re

from compiler_core import compile_post
from misc import read_file, write_file, done, nothing_to_do
from readable_queries import get_all_nodes
from sqlbase import BlogPost

from sqlalchemy import desc
from sqlalchemy.sql.expression import func


def create_node_definitions() -> dict:
    regexes_and_corresponding_ids = dict()

    # Apply longest term first: Prefer "world spirit" over "spirit"
    for node in get_all_nodes().order_by(desc(func.lenth(BlogPost.name))):
        regex = re.compile(re.escape(node.name), flags=re.IGNORECASE)
        regexes_and_corresponding_ids[node.name] = (regex, node.id)

    return regexes_and_corresponding_ids


def create_node_interstage(definitions: dict, node: BlogPost) -> None:
    # The interstage is the user markdown with the
    # node references mixed in. This interstage is
    # what will then be turned into html.

    markdown = read_file(node.markdown_path)
    for word, (regex, target_node_id) in definitions.items():
        if word == node.name:
            continue

        # Turn word into syntax [word]({{ post: X }})
        markdown = regex.sub(rf"[\g<0>]({{{{ post: {target_node_id} }}}})", markdown)

    write_file(node.interstage_path, markdown)


def compile_all_graph_pages() -> None:
    print("Compiling graph pages...")
    definitions = create_node_definitions()
    if nodes := get_all_nodes().all():
        for node in nodes:
            print(f"Compiling graph page \"{node.name}\"... ", end="", flush=True)
            create_node_interstage(definitions, node)
            compile_post(node)
            done()
        done()

    else:
        nothing_to_do()
