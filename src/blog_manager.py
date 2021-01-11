#!/usr/bin/env python3
import sys

from sqlbase import db, Author


BANNER = """\
-=[ Blog Manager ]=-
"""


def create_author() -> None:
    name = input("Name: ")
    biography = input("Biography: ")

    author = Author(name, biography)
    db.add(author)
    db.commit()


def show_authors() -> None:
    print("Currently registered authors:")
    for author in db.query(Author):
        print(f" ({author.id}) - \"{author.name}\"")


def delete_author() -> None:
    author_id = int(input("Author ID: "))
    author = db.query(Author).filter_by(id=author_id).first()
    if author:
        for blog_post in author.blog_posts:
            print(f"Deleted post \"{blog_post.title}\".")
            db.delete(blog_post)

        db.delete(author)
        db.commit()
        print(f"Deleted author \"{author.name}\".")
    else:
        print(f"No author with ID: {author_id}.")


def create_blog_post() -> None:
    print("Creating Blog Post")


def show_blog_posts() -> None:
    print("Showing Blog Posts")


def delete_blog_post() -> None:
    print("Deleting Blog Post")


def exit_program() -> None:
    print("Exiting...")


def main() -> None:
    print(BANNER)

    options = [
        ("Create Author", create_author),
        ("Show Authors", show_authors),
        ("Delete Author", delete_author),
        ("Create Blog Post", create_blog_post),
        ("Show Blog Posts", show_blog_posts),
        ("Delete Blog Post", delete_blog_post),
        ("Exit", exit_program),
    ]

    for i in range(len(options)):
        print(f" ({i + 1}) - {options[i][0]}")

    print()
    selected_option = int(input("Enter Option: ") or str(len(options))) - 1
    print()
    if 0 <= selected_option < len(options):
        options[selected_option][1]()  # Execute option
        sys.exit(0)

    print("Invalid option.")
    sys.exit(-1)


if __name__ == "__main__":
    main()
