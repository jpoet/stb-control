from pathlib import Path
import time

from stb_control.logger import log

def register_handler(handler_type: str, domain: str):
    """Decorator to mark a method for a specific handler type and domain.

    Can be stacked to register multiple domains to the same method.
    """
    def decorator(func):
        # Initialize metadata container if this is the first decorator running
        if not hasattr(func, "_handler_meta"):
            func._handler_meta = {
                "type": handler_type,
                "domains": []
            }

        # Append the current domain to the list
        func._handler_meta["domains"].append(domain)
        return func
    return decorator


class STB:
    def __init__(self, device_name):
        self.device_name = device_name

        self.link_handlers = {}
        self.prologue_handlers = {}
        self.epilogue_handlers = {}

        registry_map = {
            "link": self.link_handlers,
            "prologue": self.prologue_handlers,
            "epilogue": self.epilogue_handlers
        }

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_handler_meta"):
                meta = attr._handler_meta
                h_type = meta["type"]
                domains = meta["domains"]  # A list from the stacked decorators

                if h_type in registry_map:
                    # Map every domain in the list to this method
                    for domain in domains:
                        registry_map[h_type][domain] = attr
                else:
                    log.warn(f"Unknown handler type '{h_type}' on method {attr_name}")

        # https://www.disneyplus.com/play/14cbe24d-a931-46d6-b805-ac9893167a88
        # https://tv.youtube.com/watch/Kln08tZecgI
        # https://www.amazon.com/gp/video/detail/B0754PGXM5?ref_=atv_hm_hom_c_DG705c9d_3_3
        # Automatically discover all decorated methods on this instance

    def sleep(self, dur : float, loglevel = 'INFO'):
        time.sleep(dur)

    def Wait(self, value : float):
        time.sleep(value)

    def needs_update(self, filename: str, max_age_hours: float = 12.0) -> bool:
        """
        Return True if the file does not exist or has not been modified within
        max_age_hours. If True is returned, the file's timestamp is updated
        (or the file is created if it does not exist).

        Returns:
            True  - file was missing or stale (and has been touched)
            False - file is recent
        """
        path = Path(filename)
        now = time.time()
        max_age = max_age_hours * 3600

        try:
            mtime = path.stat().st_mtime
            if now - mtime < max_age:
                return False
        except FileNotFoundError:
            pass

        # File is missing or stale; update its timestamp.
        path.touch(exist_ok=True)
        return True

    def DeepLink(self, link: str, args=None):
        log.info(f"Cleaning up link '{link}'")
        if len(link) > 1 and link[0] == '"' and link[-1] == '"':
            link = link[1:-1]
            log.info(f"Cleaning up link '{link}'")

        parts = link.split('/')
        if len(parts) < 3:
            log.error("Invalid URL format")
            return False

        if not parts[0].startswith("http"):
            service = parts[0].split(':')[0]
        else:
            service = parts[2]  # e.g., "youtube.com"

        content_type = parts[1]

        for idx in range(3):
            nav_keys = self.LaunchLink(service, link, content_type)
            if nav_keys is None:
                return False

            if len(nav_keys) > 0:
                self.Keys(nav_keys)

            for idx in range(3):
                if self.MediaState() not in ["IDLE", "UNKNOWN"]:
                    break
                log.info("On landing page")
                self.Keys('select')
                self.sleep(3 + idx)
            else:
                log.info("Failed to start video")
                self.sleep(5)
                continue

            for idx in range(3):
                if self.MediaState() == "PLAYING":
                    break
                log.info("Video is paused")
                self.Keys('select')
                self.sleep(3 + idx)
            else:
                log.info("Failed to start video")
                self.sleep(5)
                continue

            break
        else:
            return False

        return True
