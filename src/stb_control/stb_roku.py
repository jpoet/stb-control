# stb_roku.py

from stb_control.logger import log
import time
import shlex
import sys
import re

import xml.etree.ElementTree as ET

from stb_control.stb_base import STB, register_handler

try:
    from roku import Roku
except ImportError:
    print('Requires https://pypi.org/project/roku/\n'
          'pip install wheel roku')

    sys.exit(-1)

class RokuSTB(STB):
    def __init__(self, name):
        # Initialize the underlying Roku library connection
        self.device_name = name
        self.device = Roku(name)

        # Triggers the base class dir(self) discovery to register handlers below
        super().__init__(name)

    def SendString(self, msg, args = None):
        log.info(f"Sending '{msg}'")
        self.device.literal(msg)
        return True

    def Play(self):
        for idx in range(5):
            if self.MediaState() == "PLAYING":
                return True
            log.info("Video is paused")
            getattr(self.device, 'select')()
            self.sleep(0.5)
        log.error("Video failed to play")
        return False

    def Keys(self, keys, args=None, delay=0.1):

        if isinstance(keys, str):
            keys = shlex.split(keys)

        idx = 0
        cnt = len(keys)

        while idx < cnt:
            cmd = keys[idx]

            if cmd.casefold() == "help":
                print(self.device.commands)
                return True

            if cmd.casefold() == "wait":
                idx += 1
                value = keys[idx]
                log.info(f"Wait {value}")
                self.sleep(float(value))

            elif cmd.casefold() == "string":
                idx += 1
                msg = keys[idx]
                self.SendString(msg)

            elif cmd.casefold() == "sync":
                idx += 1
                value = keys[idx]
                sync = getattr(self.device, "Sync", None)
                if sync:
                    log.info(f"Sync {value}")
                    sync(float(value))

            elif cmd.casefold() == "play":
                self.Play()

            else:
                value = keys[idx + 1] if idx + 1 < cnt else None

                if value and value.isnumeric():
                    idx += 1
                    log.info(f"{cmd} repeated({value})")

                    try:
                        for repeat in range(int(value)):
                            getattr(self.device, cmd)()
                            self.sleep(delay)

                        if cmd == 'home':
                            getattr(self.device, 'left')()
                            self.sleep(delay)

                    except Exception as e:
                        log.error(f"Failed to process key '{cmd}' : {e}")

                else:
                    log.info(f"{cmd}")

                    try:
                        getattr(self.device, cmd)()
                        self.sleep(delay, 'DEBUG')

                        if cmd == 'home':
                            getattr(self.device, 'left')()
                            self.sleep(delay)

                    except Exception as e:
                        log.error(f"Failed to process key '{cmd}' : {e}")

            idx += 1

        return True

    def Home(self, val = None, args = None):
        log.info('Going home')
        return self.Keys("home 2 left", delay=0.75)

    def Reset(self, val = None, args = None):
        return self.Home(val, args);

    def Reboot(self, val = None, args = None):
        log.info('Rebooting roku')
        return self.Keys("home up right up right up 2 right down right select",
                         delay=0.5)

    def Wait(self, val : float, args = None):
        self.sleep(val)

    def MediaState(self, val = None, args = None):
        for idx in range(3):
            try:
                raw_xml = self.device._get("/query/media-player")
                break
            except Exception as e:
                log.warn(f"Failed to retrieve playing status: {e}")
                self.sleep(1)
        else:
            return "UNKNOWN"

        """
        try:
            chan_xml = self.device._get("/query/tv-active-channel")
            root = ET.fromstring(chan_xml)
            msg = ET.tostring(root, encoding="utf-8").decode("utf-8")
            log.info(f"Channel: {msg}")
        except Exception as e:
            log.warn(f"Failed to retrieve channel info: {e}")
        """

        root = ET.fromstring(raw_xml)
        msg = ET.tostring(root, encoding="utf-8").decode("utf-8")
        log.debug(f"\n{msg}")

        raw_state = root.get("state")

        pos_node = root.find("position")
        dur_node = root.find("duration")

        if pos_node is not None:
            position_ms = int(pos_node.text.split()[0])
        else:
            position_ms = 0
        if dur_node is not None:
            duration_ms = int(dur_node.text.split()[0])
        else:
            duration_ms = 0

        # 3 minutes is 180,000 ms, 4 minutes is 240,000
        if raw_state.casefold() == "play":
            if 0 < duration_ms < 240000:
                state = "IDLE"
            else:
                state = "PLAYING"
        elif raw_state.casefold().startswith("pause"):
            if 0 < duration_ms < 240000:
                state = "IDLE"
            else:
                state = "PAUSED"
        elif raw_state.casefold() in ["close", "stop", None]:
            state = "IDLE"
        else:
            state = "UNKNOWN"

        log.info(f"Roku Status:{state} Position:{position_ms}ms Duration:{duration_ms}ms")

        return state

    @register_handler('prologue', 'amazon')
    def amazon_prologue(self):
        return ' wait 10 '

    @register_handler('epilogue', 'amazon')
    def amazon_epilogue(self):
        # First line may trigger "skip". Third line goes back to the beginning.
        return ('up 3 wait 0.25 down 2 wait 0.25 left wait 0.25 select wait 2 '
                'right 4 select wait 5 play '
                'up 3 wait 0.25 down 2 wait 0.25 left wait 0.25 select play wait 0.5')


    @register_handler('prologue', 'disney')
    def disney_prologue(self):
        return ' wait 15 '

    @register_handler('epilogue', 'disney')
    def disney_epilogue(self):
        return 'down 2 wait 1 left wait 1 select wait 0.75'

    def Prologue(self, service, args = None):
        prologue = self.prologue_handlers.get(service)
        if prologue:
            try:
                log.info(f"{service} Prologue")
                return self.Keys(prologue())
            except Exception as e:
                log.error(f"Error running prologue for {service}: {e}")
        return False

    def Epilogue(self, service, args = None):
        epilogue = self.epilogue_handlers.get(service)
        if epilogue:
            try:
                log.info(f"{service} Epilogue")
                return self.Keys(epilogue())
            except Exception as e:
                log.error(f"Error running epilogue for {service}: {e}")
        return False

    def parse_link_id(self, keyword, url):
        if keyword is None:
            # aiv://B0GNSXWBWG or aiv:/live/B0GNSXWBWG
            try:
                return '/'.join(url.split("/")[2:])
            except Exception as e:
                log.exception(f"url:{url} : {e}")

        pattern = fr'(?<={keyword}/)[^/?]+'
        match = re.search(pattern, url)

        if match is not None:
            show_id = match.group(0)
            log.info(f"Extracted ID: {show_id}")
            return show_id

        return None

    @register_handler('link', 'victory')
    def victory_link(self, link, content_type):
        show_id = link
        search = show_id.split('/')[-1] if '/' in show_id else show_id
        nav = f'left 3 up 3 select wait 3 string "{search}" '
        nav += f'wait 3 right 4 wait 1 select wait 2 select wait 3'
        link_type = 'live'
        return {'app'  : "Victory+",
                'type' : link_type,
                'id'   : show_id,
                'keys' : nav}

    @register_handler('link', 'nwsl')
    @register_handler('link', 'www.nwslsoccer.com')
    def nwsl_link(self, link, content_type):
        # https://www.nwslsoccer.com/match/98c13cd2f1554ce0ba2aca6de0766735/north-carolina-courage-vs-seattle-reign
        show_id = link
        search = show_id.split('/')[-1] if '/' in show_id else show_id
        # Make sure we are "home" within the app
        nav = 'left 6 wait 1 left up 4 down 1 select wait 5'
        # Move to search
        nav += ' left wait 1 down 4 up 1 select wait 2 select wait 2 '
        # Search for match
        nav += f' string "{search}" wait 2 down 4 select '
        # Limit results to Live
        nav += ' wait 2 down right select wait 2 right select wait 2 select wait 2 back wait 2 back '
        # Now select first (hopefully correct) episode
        nav += ' wait 2 down wait 2 select '

        link_type = 'live'
        return {'app'  : "NWSL+",
                'type' : link_type,
                'id'   : show_id,
                'keys' : nav}

    @register_handler('link', 'www.espn.com')
    def espn_link(self, link, content_type):
        #https://www.espn.com/watch/player/_/id/d672495a-7ff0-4410-a4f3-a7946db3296f#bucketId=5
        show_id = self.parse_link_id('id', link)
        content_type if len(content_type) > 0 else 'live'
        link_type = content_type if len(content_type) > 0 else 'episode'
        return {'app' : 'ESPN',
                'type' : link_type,
                'id'   : show_id,
                'keys' : ""}

    @register_handler('link', 'youtubetv')
    @register_handler('link', 'tv.youtube.com')
    def tv_youtube_link(self, link, content_type):
        # watch/Kln08tZecgI
        show_id = self.parse_link_id('watch', link)
        if show_id is None:
            # youtubetv://tRUbi4uHhKA
            show_id = self.parse_link_id(None, link)

        link_type = content_type if len(content_type) > 0 else 'episode'
        return {'app'  : "YouTube TV",
                'type' : link_type,
                'id'   : show_id,
                'keys' : ""}


    @register_handler('link', 'www.disneyplus.com')
    def disney_link(self, link, content_type):
        # play/14cbe24d-a931-46d6-b805-ac9893167a88
        show_id = self.parse_link_id('play', link)
        if show_id is None:
            show_id = self.parse_link_id(None, link)
        if show_id is None:
            log.error(f"No ID found: {link}")
            return None

        link_type = content_type if len(content_type) > 0 else 'movie'
        nav_keys = "select wait 15 select wait 5"
        return {'app'   : "Disney Plus",
                'type'  : link_type,
                'id'    : show_id,
                'keys'  : nav_keys}


    @register_handler('link', 'www.paramountplus.com')
    def paramount_link(self, link, content_type):
        # shows/video/024nWQfVtByAvsmL1X4cFvAFXYmZC2kr/
        show_id = self.parse_link_id('video', link)
        if show_id is None:
            log.error(f"No ID found: {link}")
            return None

        link_type = content_type if len(content_type) > 0 else 'episode'
        nav_keys = "wait 10 select wait 5"
        return {'app'   : "Paramount Plus",
                'type'  : link_type,
                'id'    : show_id,
                'keys'  : nav_keys}


    @register_handler('link', 'roku')
    @register_handler('link', 'therokuchannel.roku.com')
    def roku_link(self, link, content_type):
        # https://therokuchannel.roku.com/details/b74ef35a5e5c9dbb33cfe901a1f5efeb/nwsl-orlando-pride-vs-houston-dash
        show_id = self.parse_link_id('details', link)
        if show_id is None:
            show_id = self.parse_link_id(None, link)

        link_type = content_type if len(content_type) > 0 else 'liveFeed'
        nav_keys = 'wait 10'
        return {'app'   : "The Roku Channel",
                'type'  : link_type,
                'id'    : show_id,
                'keys'  : nav_keys}


    @register_handler('link', 'aiv')
    @register_handler('link', 'www.amazon.com')
    def amazon_link(self, link, content_type):
        # gp/video/detail/B0GNSXWBWG/ref=atv_hm_spo_c_7n71ba_eWFbka_1_1?jic=16%7CCgNhbGwSA2FsbA%3D%3D
        show_id = self.parse_link_id('detail', link)
        if show_id is None:
            # aiv://B0GNSXWBWG or aiv:/live/B0GNSXWBWG
            show_id = self.parse_link_id(None, link)

        link_type = content_type if len(content_type) > 0 else 'episode'
        if link_type == 'live':
            nav_keys  = 'select wait 14 down 2 select'
        else:
#            nav_keys  = 'select wait 10 select wait 5'
            nav_keys  = 'select wait 10'

        return {'app'  : "Prime Video",
                'type' : link_type,
                'id'   : show_id,
                'keys' : nav_keys}

    """
    media types:

    movie: A long-form film or movie (typically over 15 minutes). Launches directly into playback.

    episode: A single episode of a TV show. Launches the specific episode directly into playback.

    series: A set of related serialized episodes (e.g., a TV show). Triggers smart playback based on the user's viewing history and chronological progress (e.g., picks up the next unwatched episode).

    season: A specific group of episodes within a series. Opens to a content springboard showing episodes organized by the selected season, highlighting the deep-linked episode.

    shortFormVideo: Standalone short-form content. Typically under 15 minutes (e.g., trailers, news or comedy clips, food reviews).

    tvSpecial: One-time TV programs that do not fit into a standard series, or unclassified content (e.g., non-episodic news specials, music, sporting events).

    liveFeed: A live linear stream.sportsEvent: A live sporting event.
    """

    def LaunchLink(self, service, link, content_type):
        if service not in self.link_handlers:
            log.error(f"Failed to find deep link method for {service}")
            return None
        handler = self.link_handlers[service]
        params = handler(link, content_type)
        if params is None:
            return None

        self.Home()

        tv = self.device[params['app']]
        try:
            log.info(f"Launching {params['app']} for {params['type']} "
                     f": {params['id']}")
            self.device.launch(tv, {"contentId": params['id'],
                                    "mediaType": params['type']})

            self.sleep(10)
            for slp in range(10):
                if self.device.active_app.name == params['app']:
                    log.info(f"{self.device.active_app.name} running")
                    return params['keys']
                log.info(f"Current {self.device.active_app.name}")
                time.sleep(1)
        except Exception as e:
            log.exception(f"Deep link failed : {e}")
            self.device.launch(tv, {"contentId": params['id'],
                                    "mediaType": "event"})

        return None
