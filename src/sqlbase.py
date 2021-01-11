from datetime import datetime

from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, index=True, nullable=False, default="")
    biography = Column(String, nullable=False, default="")

    blog_posts = relationship("BlogPost", back_populates="author")

    def __init__(self, name: str, biography: str) -> None:
        self.biography = biography
        self.name = name

    def __repr__(self) -> str:
        return f"Author(id=\"{self.id}\", name=\"{self.name}\")"


class BlogPost(Base):
    __tablename__ = "blogposts"

    id = Column(Integer, primary_key=True)
    hits = Column(Integer, default=0)
    title = Column(String, unique=True, index=True, nullable=False, default="")
    timestamp = Column(DateTime, default=datetime.utcnow())

    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="blog_posts")

    @property
    def slug(self) -> str:
        return self.title.replace(" ", "-")

    @property
    def slug_path(self) -> str:
        return f"blogposts/{self.slug}"

    @property
    def css_path(self) -> str:
        return f"{self.slug_path}/post.css"

    @property
    def html_path(self) -> str:
        return f"{self.slug_path}/post.html"

    def __init__(self, title: str, author_id: int) -> None:
        self.author_id = author_id
        self.title = title

    def __repr__(self) -> str:
        return f"BlogPost(id=\"{self.id}\", title=\"{self.title}\")"


def create_session(path: str) -> any:
    engine = create_engine("sqlite:///" + path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


db = create_session("blog.db")
