from sqlalchemy import create_engine, Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BlogPost(Base):
    __tablename__ = "blogposts"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False, default="")

    hits = Column(Integer, default=0)

    title = Column(String, unique=True, index=True, nullable=False, default="")
    author = Column(String, unique=True, index=True, nullable=False, default="")

    def __init__(self, path: str, title: str, author: str) -> None:
        self.author = author
        self.title = title
        self.path = path

    def __repr__(self):
        return f"BlogPost(id=\"{self.id}\", title=\"{self.title}\")"


def create_session(path: str) -> any:
    engine = create_engine("sqlite:///" + path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


db = create_session("blog.db")
