import logging

from datetime import datetime, timedelta
from typing import Callable


# How long a visitors IP address should be retained in the IP tracker.
MAX_IP_RETENTION_TIME = timedelta(hours=12)


class FileCache:
    """Keep file contents in memory to avoid file system slowness."""
    cache = dict()

    def get_contents(self, path: str) -> str:
        if path in self.cache:
            return self.cache[path]

        logging.debug(f"FileCache: Reading file \"{path}\"...")
        with open(path, "r") as f:
            return self.cache.setdefault(path, f.read())


class IPTracker:
    """Keeps track of recent (IP address, post id) tuples to make hit counting a bit less wonky"""
    recorded_hits = dict()

    def remove_expired(self) -> None:
        to_pop = list()
        for key, timestamp in self.recorded_hits.items():
            if datetime.now() - timestamp > MAX_IP_RETENTION_TIME:
                to_pop.append(key)

        # Alter dict afterwards to avoid a RuntimeError
        if to_pop:
            logging.debug(f"IPTracker: Purging records {to_pop}...")
            for pop in to_pop:
                self.recorded_hits.pop(pop)

    def should_count_request(self, ip: str, post_id: int) -> bool:
        key = (ip, post_id)
        was_not_in_hits_previously = key not in self.recorded_hits
        self.recorded_hits[key] = datetime.now()
        return was_not_in_hits_previously


def static_vars(**kwargs) -> Callable:
    """A decorator to make function-static variables a bit prettier"""
    def decorate(func: Callable) -> Callable:
        for key in kwargs:
            setattr(func, key, kwargs[key])
        return func

    return decorate
