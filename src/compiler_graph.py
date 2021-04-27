import re

from compiler_core import compile_post
from misc import read_file, write_file, done, first_word_in_string
from readable_queries import get_all_nodes
from sqlbase import BlogPost


def create_node_definitions() -> dict:
    regexes_and_corresponding_ids = dict()
    for blog_post in get_all_nodes():
        node_name = first_word_in_string(blog_post.name)
        regex = re.compile(re.escape(node_name), flags=re.IGNORECASE)
        regexes_and_corresponding_ids[node_name] = (regex, blog_post.id)

    return regexes_and_corresponding_ids


def create_node_interstage(definitions: dict, node: BlogPost) -> None:
    # The interstage is the user markdown with the
    # node references mixed in. This interstage is
    # what will then be turned into html.

    markdown = read_file(node.markdown_path)
    node_name = first_word_in_string(node.name)
    for word, (regex, target_node_id) in definitions.items():
        if word == node_name:
            continue

        # Turn word into syntax [word]({{ post: X }})
        markdown = regex.sub(rf"[\g<0>]({{{{ post: {target_node_id} }}}})", markdown)

    write_file(node.interstage_path, markdown)


def compile_all_graph_pages() -> None:
    print("Compiling graph pages...")
    definitions = create_node_definitions()
    for node in get_all_nodes():
        print(f"Compiling graph post \"{node.name}\"... ", end="", flush=True)
        create_node_interstage(definitions, node)
        compile_post(node)
        done()
