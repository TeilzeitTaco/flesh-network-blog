import re

from abc import abstractmethod
from datetime import datetime
from hashlib import sha256

from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


def get_date_suffix(date: int) -> str:
    date_suffix = ["th", "st", "nd", "rd"]
    return date_suffix[date % 10] if date % 10 in [1, 2, 3] and date not in [11, 12, 13] else date_suffix[0]


def slugify(base: str) -> str:
    return re.sub(r"[^a-zA-Z0-9-]+", "", base.replace(" ", "-"))


class Nameable:
    @property
    @abstractmethod
    def name(self) -> str:
        pass


# Aux. mapping table
class TagAssociation(Base):
    __tablename__ = "tag_associations"

    id = Column(Integer, primary_key=True)
    blog_post_id = Column(Integer, ForeignKey("blogposts.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    def __init__(self, blog_post_id: int, tag_id: int) -> None:
        self.blog_post_id = blog_post_id
        self.tag_id = tag_id

    def __repr__(self) -> str:
        return f"TagAssociation(id={self.id}, blog_post_id={self.blog_post_id}, tag_id={self.tag_id})"


class Comment(Base, Nameable):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    blog_post_id = Column(Integer, ForeignKey("blogposts.id"))
    blog_post = relationship("BlogPost", back_populates="comments")

    timestamp = Column(DateTime, default=datetime.now())

    pseudonym = Column(String, nullable=False, default="")
    comment = Column(String, unique=True, nullable=False, default="")
    tag = Column(String, nullable=False, default="")

    def __init__(self, pseudonym: str, password: str, comment: str) -> None:
        self.tag = Comment.make_tag_for_pseudonym(pseudonym, password)
        self.pseudonym = pseudonym
        self.comment = comment

    @staticmethod
    def make_tag_for_pseudonym(pseudonym: str, password: str) -> str:
        hex_digest = sha256(f"{pseudonym}#{password}".encode()).hexdigest()
        return hex_digest[:3] + hex_digest[-3:]

    @property
    def name(self) -> str:
        return f"{self.pseudonym} ({self.tag}): {self.comment[:16]}..."


class ReferrerHostname(Base, Nameable):
    __tablename__ = "hostnames"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, default="")

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"ReferrerHostname(id={self.id}, name={self.name})"


class Author(Base, Nameable):
    """Represents a person which authors posts."""
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, index=True, nullable=False, default="")
    biography = Column(String, nullable=False, default="")

    blog_posts = relationship("BlogPost", back_populates="author")

    @property
    def slug(self) -> str:
        return slugify(self.name)

    def __init__(self, name: str, biography: str) -> None:
        self.biography = biography
        self.name = name

    def __repr__(self) -> str:
        return f"Author(id={self.id}, name=\"{self.name}\")"


class Friend(Base, Nameable):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False, default="")
    link = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")

    def __init__(self, name: str, link: str, description: str) -> None:
        self.description = description
        self.name = name
        self.link = link

    def __repr__(self) -> str:
        return f"Friend(id={self.id}, name=\"{self.name}\")"


class Tag(Base, Nameable):
    """A thematic category a blog post might relate to."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False, default="")
    short_description = Column(String, nullable=False, default="")
    long_description = Column(String, nullable=False, default="")

    # If this is a section tag, a tag that is shown as its own
    # category on the root page.
    main_section = Column(Boolean, default=True)

    blog_posts = relationship("BlogPost", secondary="tag_associations", order_by="BlogPost.name")

    @property
    def slug(self) -> str:
        return slugify(self.name)

    def __init__(self, name: str, short_description: str, long_description: str, main_section: bool) -> None:
        self.short_description = short_description
        self.long_description = long_description
        self.main_section = main_section
        self.name = name

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name=\"{self.name}\")"


class FileResource(Base, Nameable):
    __tablename__ = "file_resources"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, default="")
    title = Column(String, unique=True, nullable=False, default="")
    clear_name = Column(String, unique=True, index=True, nullable=False, default="")

    is_image = Column(Boolean, default=True)
    is_thumbnail = Column(Boolean, default=True)

    blog_post_id = Column(Integer, ForeignKey("blogposts.id"))
    blog_post = relationship("BlogPost", back_populates="file_resources")

    def __init__(self, name: str, clear_name: str, title: str, blog_post: any,
                 is_image: bool = False, is_thumbnail: bool = False) -> None:

        self.is_thumbnail = is_thumbnail
        self.is_image = is_image

        self.clear_name = clear_name
        self.blog_post = blog_post
        self.title = title
        self.name = name

    def __repr__(self) -> str:
        return f"FileResource(id={self.id}, name=\"{self.name}\")"


class BlogPost(Base, Nameable):
    __tablename__ = "blogposts"

    id = Column(Integer, primary_key=True)
    hits = Column(Integer, default=0)
    name = Column(String, unique=True, index=True, nullable=False, default="")  # Title but called "name" for interface
    timestamp = Column(DateTime, default=datetime.now())

    # defaults for     | graph pages | blog posts |
    # include_in_graph |      x      |            | if this is a graph page or a blog post
    # allow_comments   |             |     x      | if viewers can post comments
    # hidden           |      x      |            | if this post can be shown in "Recent Posts" or the post index

    # Graph pages generally hold descriptions for overarching
    # thoughts and concepts. They are automatically annotated
    # with references to other graph pages at compile time.

    include_in_graph = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    hidden = Column(Boolean, default=False)

    tags = relationship("Tag", secondary="tag_associations", order_by="Tag.name")

    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="blog_posts")
    comments = relationship("Comment", back_populates="blog_post")
    file_resources = relationship("FileResource", back_populates="blog_post")

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def slug_path(self) -> str:
        return f"blogposts/{self.author.slug}/{self.slug}"

    @property
    def markdown_path(self) -> str:
        return f"{self.slug_path}/post.md"

    @property
    def interstage_path(self) -> str:
        if self.include_in_graph:
            return f"{self.slug_path}/interstage.md"
        return self.markdown_path

    @property
    def resources_path(self) -> str:
        return f"{self.slug_path}/res"

    @property
    def html_path(self) -> str:
        return f"{self.slug_path}/post.html"

    @property
    def formatted_timestamp(self) -> str:
        return (self.timestamp.strftime(f"%A, the %-d{get_date_suffix(self.timestamp.day)} of %B, %Y, around %I %p")
                .replace("12 AM", "midnight")  # Imagine being british
                .replace("12 PM", "noon"))

    def __init__(self, name: str, author: Author) -> None:
        self.author = author
        self.name = name

    def __repr__(self) -> str:
        return f"BlogPost(id={self.id}, title=\"{self.name}\")"


def create_session(path: str) -> any:
    engine = create_engine("sqlite:///" + path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


db = create_session("blog.db")
