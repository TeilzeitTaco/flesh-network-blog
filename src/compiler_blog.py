from compiler_core import compile_post
from misc import done, lenient_error
from readable_queries import get_all_blog_posts
from sqlbase import BlogPost


def compile_blog_post(blog_post: BlogPost) -> None:
    print(f"Compiling blog post \"{blog_post.name}\"... ", end="", flush=True)
    if blog_post.include_in_graph:
        lenient_error("Cannot compile graph page individually!")
        return

    compile_post(blog_post)
    done()


def compile_all_blog_posts() -> None:
    for blog_post in get_all_blog_posts():
        compile_blog_post(blog_post)
