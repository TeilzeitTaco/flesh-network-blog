import logging

from datetime import datetime, timedelta
from typing import Callable


# How long a visitors IP address should be retained in the IP tracker.
MAX_IP_RETENTION_TIME = timedelta(minutes=15)


class FileCache:
    """Keep file contents in memory to avoid file system slowness."""
    cache = dict()

    def get_contents(self, path: str) -> str:
        if path in self.cache:
            return self.cache[path]

        logging.debug(f"FileCache: Reading file \"{path}\"...")
        with open(path, "r") as f:
            contents = f.read()
            self.cache[path] = contents
            return contents


class IPTracker:
    known_ips = dict()

    def remove_expired(self) -> None:
        to_pop = list()
        for ip, timestamp in self.known_ips.items():
            if datetime.now() - timestamp > MAX_IP_RETENTION_TIME:
                to_pop.append(ip)

        # Alter dict afterwards to avoid a RuntimeError
        if to_pop:
            logging.debug(f"IPTracker: Purging addresses {str(to_pop)}...")
            for pop in to_pop:
                self.known_ips.pop(pop)

    def should_count_request(self, ip: str) -> bool:
        if ip in self.known_ips:
            self.known_ips[ip] = datetime.now()
            return False

        self.known_ips[ip] = datetime.now()
        return True


def static_vars(**kwargs) -> Callable:
    """A decorator to make function-static variables a bit prettier"""
    def decorate(func) -> Callable:
        for key in kwargs:
            setattr(func, key, kwargs[key])
        return func

    return decorate

