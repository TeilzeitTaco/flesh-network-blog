from sqlalchemy import create_engine, Integer, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, index=True, nullable=False, default="")
    biography = Column(String, nullable=False, default="")

    blog_posts = relationship("BlogPost", back_populates="author")

    def __init__(self, name: str, biography: str):
        self.biography = biography
        self.name = name

    def __repr__(self):
        return f"Author(id=\"{self.id}\", name=\"{self.name}\")"


class BlogPost(Base):
    __tablename__ = "blogposts"

    id = Column(Integer, primary_key=True)
    html_path = Column(String, unique=True, nullable=False, default="")

    hits = Column(Integer, default=0)
    title = Column(String, unique=True, index=True, nullable=False, default="")

    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="blog_posts")

    def __init__(self, path: str, title: str, author: str) -> None:
        self.author = author
        self.title = title
        self.path = path

    def __repr__(self) -> str:
        return f"BlogPost(id=\"{self.id}\", title=\"{self.title}\")"


def create_session(path: str) -> any:
    engine = create_engine("sqlite:///" + path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


db = create_session("blog.db")
