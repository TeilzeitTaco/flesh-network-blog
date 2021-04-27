from sqlbase import db, BlogPost


def get_all_nodes() -> any:
    return db.query(BlogPost).filter_by(include_in_graph=True)


def get_all_blog_posts() -> any:
    return db.query(BlogPost).filter_by(include_in_graph=False)


def get_all_posts() -> any:
    return db.query(BlogPost)


def get_all_visible_blog_posts() -> any:
    return db.query(BlogPost).filter_by(hidden=False)
