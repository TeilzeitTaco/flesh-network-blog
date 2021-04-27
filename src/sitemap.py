import functools
import xml.etree.cElementTree as eT

from sqlbase import db, BlogPost, Author, Tag
from flask import url_for, request


XML_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"


def generate_sitemap() -> str:
    # Semi-minimal sitemap implementation according to https://www.sitemaps.org/protocol.html
    urlset = eT.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    insert_url = functools.partial(_insert_url, urlset, get_base_url())
    insert_url(loc="", priority=1)

    for post in db.query(BlogPost):
        insert_url(loc=url_for("home.route_blog_post", blog_post_id=post.id, _name=post.slug),
                   priority=0.8)

    for tag in db.query(Tag):
        insert_url(loc=url_for("home.route_tag", tag_id=tag.id, _name=tag.slug),
                   priority=0.6)

    for author in db.query(Author):
        insert_url(loc=url_for("home.route_author", author_id=author.id, _name=author.slug),
                   priority=0.4)

    return XML_HEADER + eT.tostring(urlset, encoding="unicode", method="xml")


def get_base_url() -> str:
    return request.base_url.rsplit("/", 1)[0]


def _insert_url(urlset: eT.Element, prefix: str, loc: str, priority: float) -> None:
    url = eT.SubElement(urlset, "url")
    eT.SubElement(url, "loc").text = prefix + loc
    eT.SubElement(url, "priority").text = str(priority)
