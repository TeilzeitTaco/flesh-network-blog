import os
import re

from compiler_core import compile_post
from misc import read_file, write_file, done
from sqlbase import db, BlogPost

PATH_NAME = "thought-graph"


def get_all_nodes() -> list:
    return db.query(BlogPost).filter_by(include_in_graph=True)


def create_node_definitions() -> dict:
    regexes_and_corresponding_ids = dict()
    for blog_post in get_all_nodes():
        regex = re.compile(re.escape(blog_post.name))
        regexes_and_corresponding_ids[regex] = blog_post.id

    return regexes_and_corresponding_ids


def create_node_interstage(definitions: dict, node: BlogPost) -> None:
    path = os.path.join(PATH_NAME, node.file_name)
    markdown = read_file(path)

    # The interstage is the user markdown with the
    # node references mixed in. This interstage is
    # what will then be turned into html.

    for word, target_node_id in definitions.values():
        markdown = word.sub(markdown, rf"[\0]({target_node_id})")

    write_file(node.interstage_path, markdown)


def compile_all_graph_pages() -> None:
    definitions = create_node_definitions()
    for node in get_all_nodes():
        print(f"Compiling graph post \"{node.name}\"... ", end="", flush=True)
        create_node_interstage(definitions, node)
        compile_post(node)
        done()
