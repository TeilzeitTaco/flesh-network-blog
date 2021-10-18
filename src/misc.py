import hashlib
import logging
import os
import sys

from datetime import datetime, timedelta
from typing import Callable, NoReturn, Optional

GENERATED_RESOURCES_PATH = "static/gen/res/"

# How long a visitors IP address should be retained in the IP tracker.
MAX_IP_RETENTION_TIME = timedelta(hours=24)


class FileCache:
    """Keep file contents in memory to avoid file system slowness."""
    __cache = dict()

    def get_contents(self, path: str) -> str:
        if path in self.__cache:
            return self.__cache[path]

        logging.debug(f"FileCache: Reading file \"{path}\"...")
        with open(path, "r") as f:
            return self.__cache.setdefault(path, f.read())


class IPTracker:
    """Keeps track of recent (IP address hash, post id) tuples to make hit counting a bit less wonky"""
    __recorded_hits = dict()

    def remove_expired(self) -> None:
        to_pop = list()
        for key, timestamp in self.__recorded_hits.items():
            if datetime.now() - timestamp > MAX_IP_RETENTION_TIME:
                to_pop.append(key)

        # Alter dict afterwards to avoid a RuntimeError
        if to_pop:
            for pop in to_pop:
                self.__recorded_hits.pop(pop)

    def should_count_request(self, clear_ip: str, post_id: int) -> bool:
        key = (hash_string(clear_ip), post_id)
        was_not_in_hits_previously = key not in self.__recorded_hits
        self.__recorded_hits[key] = datetime.now()
        return was_not_in_hits_previously


def static_vars(**kwargs) -> Callable:
    """A decorator to make function-static variables a bit prettier"""
    def decorate(func: Callable) -> Callable:
        for key in kwargs:
            setattr(func, key, kwargs[key])
        return func

    return decorate


def done() -> None:
    print("Done!")


def critical_error(message: str) -> NoReturn:
    print(f"Critical Error!\n{message}")
    sys.exit(-1)


def lenient_error(message: str) -> None:
    print(f"Error!\n{message}")


def nothing_to_do() -> None:
    print("Nothing to do!")


def read_file(path: str) -> str:
    if not os.path.exists(path):
        critical_error(f"Missing file: \"{path}\"!")

    with open(path, "r", encoding="latin-1") as f:
        return f.read().strip()


def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def hash_file(path: str, length: int = 32) -> str:
    with open(path, "rb") as f:
        hash_sum = hashlib.shake_256()
        hash_sum.update(f.read())

    return hash_sum.hexdigest(length)


def hash_string(string: str, length: int = 32) -> str:
    hash_sum = hashlib.shake_256()
    hash_sum.update(string.encode())
    return hash_sum.hexdigest(length)


def has_prefix(string: str, prefix: str) -> Optional[str]:
    if string.lower().startswith(prefix.lower()):
        return string[len(prefix):].strip()


def in_res_path(path: str) -> str:
    return GENERATED_RESOURCES_PATH + path


def file_name_to_title(file_name: str) -> str:
    return " ".join(file_name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").split()).title()

