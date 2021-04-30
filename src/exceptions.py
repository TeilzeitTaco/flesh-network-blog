class BlogManagerException(Exception):
    pass


class PostNotFoundException(BlogManagerException):
    pass


class CancelledException(BlogManagerException):
    pass
