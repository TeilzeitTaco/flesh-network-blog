import re

from datetime import datetime

from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


def get_date_suffix(date: int) -> str:
    date_suffix = ["th", "st", "nd", "rd"]
    return date_suffix[date % 10] if date % 10 in [1, 2, 3] and date not in [11, 12, 13] else date_suffix[0]


def slugify(base: str) -> str:
    return re.sub(r"[^a-zA-Z0-9-]+", "", base.replace(" ", "-"))


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


class Author(Base):
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


class Tag(Base):
    """A thematic category a blog post might relate to."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False, default="")

    blog_posts = relationship("BlogPost", secondary="tag_associations")

    @property
    def slug(self) -> str:
        return slugify(self.name)

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name=\"{self.name}\""


class BlogPost(Base):
    __tablename__ = "blogposts"

    id = Column(Integer, primary_key=True)
    hits = Column(Integer, default=0)
    name = Column(String, unique=True, index=True, nullable=False, default="")  # Title but called "name" for reflection
    timestamp = Column(DateTime, default=datetime.now())

    tags = relationship("Tag", secondary="tag_associations")

    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="blog_posts")

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def slug_path(self) -> str:
        return f"blogposts/{self.slug}"

    @property
    def markdown_path(self) -> str:
        return f"{self.slug_path}/post.md"

    @property
    def resources_path(self) -> str:
        return f"{self.slug_path}/res"

    @property
    def html_path(self) -> str:
        return f"{self.slug_path}/post.html"

    @property
    def formatted_timestamp(self) -> str:
        return self.timestamp.strftime(f"%A, the %d{get_date_suffix(self.timestamp.day)} of %B, %Y, around %I %p")

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
