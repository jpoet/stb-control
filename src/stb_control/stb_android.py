# android_stb.py

from stb_control.logger import log

import json
from pathlib import Path
import warnings
import sys
import re

try:
    from adb_shell.adb_device import AdbDeviceTcp
    from adb_shell.auth.sign_pythonrsa import PythonRSASigner
    from adb_shell.auth.keygen import keygen
except Exception as e:
    print(f"{e} Requires adb_shell: sudo dnf install python3-adb-shell")
    sys.exit(-1)


from stb_control.stb_base import STB, register_handler

class AndroidSTB(STB):
    def __init__(self, name):
        self.device_name = name
        self.device = self.open_device()

        self.adb_keys = {
            "key_events": {
                "key_null": 0,
                "key_soft_left": 1,
                "key_soft_right": 2,
                "key_home": 3,
                "key_back": 4,
                "key_call": 5,
                "key_endcall": 6,
                "key_0": 7,
                "key_1": 8,
                "key_2": 9,
                "key_3": 10,
                "key_4": 11,
                "key_5": 12,
                "key_6": 13,
                "key_7": 14,
                "key_8": 15,
                "key_9": 16,
                "key_star": 17,
                "key_pound": 18,
                "key_dpad_up": 19,
                "key_dpad_down": 20,
                "key_dpad_left": 21,
                "key_dpad_right": 22,
                "key_dpad_center": 23,
                "key_volume_up": 24,
                "key_volume_down": 25,
                "key_power": 26,
                "key_camera": 27,
                "key_clear": 28,
                "key_a": 29,
                "key_b": 30,
                "key_c": 31,
                "key_d": 32,
                "key_e": 33,
                "key_f": 34,
                "key_g": 35,
                "key_h": 36,
                "key_i": 37,
                "key_j": 38,
                "key_k": 39,
                "key_l": 40,
                "key_m": 41,
                "key_n": 42,
                "key_o": 43,
                "key_p": 44,
                "key_q": 45,
                "key_r": 46,
                "key_s": 47,
                "key_t": 48,
                "key_u": 49,
                "key_v": 50,
                "key_w": 51,
                "key_x": 52,
                "key_y": 53,
                "key_z": 54,
                "key_comma": 55,
                "key_period": 56,
                "key_alt_left": 57,
                "key_alt_right": 58,
                "key_shift_left": 59,
                "key_shift_right": 60,
                "key_tab": 61,
                "key_space": 62,
                "key_sym": 63,
                "key_explorer": 64,
                "key_envelope": 65,
                "key_enter": 66,
                "key_del": 67,
                "key_grave": 68,
                "key_minus": 69,
                "key_equals": 70,
                "key_left_bracket": 71,
                "key_right_bracket": 72,
                "key_backslash": 73,
                "key_semicolon": 74,
                "key_apostrophe": 75,
                "key_slash": 76,
                "key_at": 77,
                "key_num": 78,
                "key_headsethook": 79,
                "key_focus": 80,
                "key_plus": 81,
                "key_menu": 82,
                "key_notification": 83,
                "key_search": 84,
                "key_media_play_pause": 85,
                "key_media_stop": 86,
                "key_media_next": 87,
                "key_media_previous": 88,
                "key_media_rewind": 89,
                "key_media_fast_forward": 90,
                "key_mute": 91,
                "key_page_up": 92,
                "key_page_down": 93,
                "key_pictsymbols": 94,
                "key_switch_charset": 95,
                "key_button_a": 96,
                "key_button_b": 97,
                "key_button_c": 98,
                "key_button_x": 99,
                "key_button_y": 100,
                "key_button_z": 101,
                "key_button_l1": 102,
                "key_button_r1": 103,
                "key_button_l2": 104,
                "key_button_r2": 105,
                "key_button_thumbl": 106,
                "key_button_thumbr": 107,
                "key_button_start": 108,
                "key_button_select": 109,
                "key_button_mode": 110,
                "key_escape": 111,
                "key_forward_del": 112,
                "key_ctrl_left": 113,
                "key_ctrl_right": 114,
                "key_caps_lock": 115,
                "key_scroll_lock": 116,
                "key_meta_left": 117,
                "key_meta_right": 118,
                "key_function": 119,
                "key_sysrq": 120,
                "key_break": 121,
                "key_move_home": 122,
                "key_move_end": 123,
                "key_insert": 124,
                "key_forward": 125,
                "key_media_play": 126,
                "key_media_pause": 127,
                "key_media_close": 128,
                "key_media_eject": 129,
                "key_media_record": 130,
                "key_f1": 131,
                "key_f2": 132,
                "key_f3": 133,
                "key_f4": 134,
                "key_f5": 135,
                "key_f6": 136,
                "key_f7": 137,
                "key_f8": 138,
                "key_f9": 139,
                "key_f10": 140,
                "key_f11": 141,
                "key_f12": 142,
                "key_num_lock": 143,
                "key_numpad_0": 144,
                "key_numpad_1": 145,
                "key_numpad_2": 146,
                "key_numpad_3": 147,
                "key_numpad_4": 148,
                "key_numpad_5": 149,
                "key_numpad_6": 150,
                "key_numpad_7": 151,
                "key_numpad_8": 152,
                "key_numpad_9": 153,
                "key_numpad_divide": 154,
                "key_numpad_multiply": 155,
                "key_numpad_subtract": 156,
                "key_numpad_add": 157,
                "key_numpad_dot": 158,
                "key_numpad_comma": 159,
                "key_numpad_enter": 160,
                "key_numpad_equals": 161,
                "key_numpad_left_paren": 162,
                "key_numpad_right_paren": 163,
                "key_volume_mute": 164,
                "key_info": 165,
                "key_channel_up": 166,
                "key_channel_down": 167,
                "key_zoom_in": 168,
                "key_zoom_out": 169,
                "key_tv": 170,
                "key_window": 171,
                "key_guide": 172,
                "key_dvr": 173,
                "key_bookmark": 174,
                "key_captions": 175,
                "key_settings": 176,
                "key_tv_power": 177,
                "key_tv_input": 178,
                "key_stb_power": 179,
                "key_stb_input": 180,
                "key_avr_power": 181,
                "key_avr_input": 182,
                "key_prog_red": 183,
                "key_prog_green": 184,
                "key_prog_yellow": 185,
                "key_prog_blue": 186,
                "key_app_switch": 187,
                "key_button_1": 188,
                "key_button_2": 189,
                "key_button_3": 190,
                "key_button_4": 191,
                "key_button_5": 192,
                "key_button_6": 193,
                "key_button_7": 194,
                "key_button_8": 195,
                "key_button_9": 196,
                "key_button_10": 197,
                "key_button_11": 198,
                "key_button_12": 199,
                "key_button_13": 200,
                "key_button_14": 201,
                "key_button_15": 202,
                "key_button_16": 203,
                "key_language_switch": 204,
                "key_manner_mode": 205,
                "key_3d_mode": 206,
                "key_contacts": 207,
                "key_calendar": 208,
                "key_music": 209,
                "key_calculator": 210,
                "key_zenkaku_hankaku": 211,
                "key_eisu": 212,
                "key_muhenkan": 213,
                "key_henkan": 214,
                "key_katakana_hiragana": 215,
                "key_yen": 216,
                "key_ro": 217,
                "key_kana": 218,
                "key_assist": 219,
                "key_brightness_down": 220,
                "key_brightness_up": 221,
                "key_media_audio_track": 222,
                "key_sleep": 223,
                "key_wakeup": 224,
                "key_pairing": 225,
                "key_media_top_menu": 226,
                "key_11": 227,
                "key_12": 228,
                "key_last_channel": 229,
                "key_tv_data_service": 230,
                "key_voice_assist": 231,
                "key_tv_radio_service": 232,
                "key_tv_teletext": 233,
                "key_tv_number_entry": 234,
                "key_tv_terrestrial_analog": 235,
                "key_tv_terrestrial_digital": 236,
                "key_tv_satellite": 237,
                "key_tv_satellite_bs": 238,
                "key_tv_satellite_cs": 239,
                "key_tv_satellite_service": 240,
                "key_tv_network": 241,
                "key_tv_antenna_cable": 242,
                "key_tv_input_hdmi_1": 243,
                "key_tv_input_hdmi_2": 244,
                "key_tv_input_hdmi_3": 245,
                "key_tv_input_hdmi_4": 246,
                "key_tv_input_composite_1": 247,
                "key_tv_input_composite_2": 248,
                "key_tv_input_component_1": 249,
                "key_tv_input_component_2": 250,
                "key_tv_input_vga_1": 251,
                "key_tv_audio_description": 252,
                "key_tv_audio_description_mix_up": 253,
                "key_tv_audio_description_mix_down": 254,
                "key_tv_zoom_mode": 255,
                "key_tv_contents_menu": 256,
                "key_tv_media_context_menu": 257,
                "key_tv_timer_programming": 258,
                "key_help": 259,
                "key_navigate_previous": 260,
                "key_navigate_next": 261,
                "key_navigate_in": 262,
                "key_navigate_out": 263,
                "key_stem_primary": 264,
                "key_stem_1": 265,
                "key_stem_2": 266,
                "key_stem_3": 267,
                "key_dpad_up_left": 268,
                "key_dpad_down_left": 269,
                "key_dpad_up_right": 270,
                "key_dpad_down_right": 271,
                "key_media_skip_forward": 272,
                "key_media_skip_backward": 273,
                "key_media_step_forward": 274,
                "key_media_step_backward": 275,
                "key_soft_sleep": 276,
                "key_cut": 277,
                "key_copy": 278,
                "key_paste": 279,
                "key_system_navigation_up": 280,
                "key_system_navigation_down": 281,
                "key_system_navigation_left": 282,
                "key_system_navigation_right": 283,
                "key_all_apps": 284,
                "key_refresh": 285
            },
            "aliases": {
                "home": "key_home",
                "up": "key_dpad_up",
                "down": "key_dpad_down",
                "left": "key_dpad_left",
                "right": "key_dpad_right",
                "select": "key_dpad_center",
        #        "select": "key_button_select",
        #        "select": "key_enter",
                "enter": "key_enter",
                "back": "key_back",
                "volume_up": "key_volume_up",
                "volume_down": "key_volume_down",
                "volume_mute": "key_volume_mute"
            }
        }
        super().__init__(name)  # Always call super() LAST

    def open_device(self):
        warnings.filterwarnings (
            action='ignore',
            category=RuntimeWarning,
            module=r'dataclasses_json'
        )

        # Load the public and private keys
        adbkey_file = Path('~mythtv/etc/adbkey').expanduser()
        if not adbkey_file.with_suffix('.pub').exists():
            keygen(str(adbkey_file))
        with open(adbkey_file) as f:
            priv = f.read()

        with open(adbkey_file.with_suffix('.pub')) as f:
            pub = f.read()
        signer = PythonRSASigner(pub, priv)

        self.device = AdbDeviceTcp(self.device_name, 5555,
                                   default_transport_timeout_s=9.)
        try:
            self.device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
        except Exception as e:
            log.error(f"Failed to connect: {e}")
            sys.exit(1)
            return None

        log.info(f"Connected to {self.device_name}")
        return self.device


    def keycode_from_alias(self, alias):
        alias = alias.casefold()
        if alias == 'null':
            return self.adb_keys['key_events']["key_null"]
        if alias == 'replay':
            return self.adb_keys['key_events']["key_dpad_left"]
        if alias == 'fast_forward' or alias == 'forward':
            return self.adb_keys['key_events']["key_media_fast_forward"]
        if alias == 'play':
            return self.adb_keys['key_events']["key_media_play"]
        if alias == 'pause':
            return self.adb_keys['key_events']["key_media_pause"]
        if alias == 'previous':
            return self.adb_keys['key_events']["key_media_previous"]
        if alias in self.adb_keys['aliases']:
            return self.adb_keys['key_events'][self.adb_keys['aliases'][alias]]
        if alias in self.adb_keys['key_events']:
            return self.adb_keys['key_events'][alias]
        if "key_" + alias in self.adb_keys['key_events']:
            return self.adb_keys['key_events']["key_" + alias]
        log.error(f"Unable to find '{alias}' in key_events")
        return None


    def SendString(self, string, args = None):
        string = string.replace(' ', '%s')
        cmd = f'input text "{string}"'
        log.info(f"{cmd}")
        self.device.shell(cmd)
        self.sleep(0.1)


    def Keys_combined(self, keys):
        """
        Don't use! Too bad it misses keys!
        """
        idx = 0
        cnt = len(keys)
        cmd = "input keyevent "
        while idx < cnt:
            key = keys[idx]
            log.info(key)
            if key.casefold() == 'wait':
                if cmd != "input keyevent ":
                    log.info(cmd)
                    self.device.shell(cmd)
                    cmd = "input keyevent "
                idx += 1
                value = keys[idx]
                log.info(f"Wait {value}")
                self.sleep(float(value))
            else:
                value = keys[idx + 1] if idx + 1 < cnt else None
                if value and value.isnumeric():
                    idx += 1
                else:
                    value = 1
                for repeat in range(int(value)):
                    code = self.keycode_from_alias(key)
                    cmd += f'{code} '

            idx += 1

        log.info(cmd)
        self.device.shell(cmd)

    def Keys(self, key_names : str, args = None, delay = 0.2):
        """
        Parse keys names from a string and then issue those key
        presses to the AndroidTV device. Allow for "wait #" between
        keypresses which results in a pause for that many seconds.
        """
        # repeat_sleep = 0.25
        keys = key_names.split()
        # keys = key_names
        log.debug(keys)

        idx = 0
        cnt = len(keys)
        while idx < cnt:
            key = keys[idx]
            if key.casefold() == "wait":
                idx += 1
                value = keys[idx]
                log.info(f"Wait {value}")
                self.sleep(float(value))
            elif key.casefold() == "string":
                idx += 1
                msg = keys[idx]
                self.SendString(msg, args)
            else:
                value = keys[idx + 1] if idx + 1 < cnt else None
                if value and value.isnumeric():
                    idx += 1
                    log.info(f"{key} repeated({value})")
                else:
                    value = 1
                for repeat in range(int(value)):
                    code = self.keycode_from_alias(key)
                    cmd = f"input keyevent {code}"
                    resp = self.device.shell(cmd)
                    log.info(f"{cmd} : {resp}")
    #                self.sleep(repeat_sleep)
            idx += 1

        return True

    def SetRefresh(self, min : float, max : float):
        cmd = 'settings put system min_refresh_rate {min}'
        cmd = 'settings put system peak_refresh_rate {max}'

        # Allow tvQuickActions Pro to adjust frame rate.
        cmd = 'adb shell pm grant co.bvi.tvquickactions android.permission.WRITE_SECURE_SETTINGS'


    def DeviceWakeup(self):
        for idx in range(3):
            cmd = 'dumpsys power'
            resp = self.device.shell(cmd)
            cmd = "input keyevent KEYCODE_WAKEUP"
            resp = self.device.shell(cmd)
            print(f"{cmd} : {resp}")
            self.sleep(0.5)

        for idx in range(3):
            cmd = 'dumpsys power'
            resp = self.device.shell(cmd)
            if 'Awake' in resp:
                break

            cmd = "input keyevent KEYCODE_WAKEUP"
            resp = self.device.shell(cmd)
            print(f"{cmd} : {resp}")
            self.sleep(0.75)
        else:
            log.warn("Failed to wake up!")
            return False

        log.debug("Awake")
        return True


    def Home(self, val = None, args = None):
        log.info('Home')
        cmd = 'input keyevent KEYCODE_HOME'
        self.device.shell(cmd)
        self.sleep(0.5)
        return True

    def Reboot(self, val = None, args = None):
        for cmd in [
                'pm trim-caches 9999999999',
                'reboot'
                ]:
            try:
                resp = self.device.shell(cmd)
                log.debug(f"{cmd} : {resp}")
            except Exception as _e:
                ...
        return True

    def Reset(self):
        apps_to_kill = set()

        # Targeted Focus Check (Bypasses messy window stacks)
        focus_dump = self.device.shell("dumpsys activity activities | grep mCurrentFocus")
        if focus_dump:
            # Matches: mCurrentFocus=Window{ec25df6 u0 tv.apmc.android.victorysports/tv...
            focus_match = re.search(r"mCurrentFocus=Window\{[a-f0-9]+\s+u\d+\s+([\w\.]+)/", focus_dump)
            if focus_match:
                apps_to_kill.add(focus_match.group(1).strip())

        # Fallback (If targeted check misses or mCurrentFocus=null)
        if not apps_to_kill:
            window_dump = self.device.shell("dumpsys window windows")
            if window_dump:
                # Scans for the absolute top visible application window in the array stack
                window_match = re.search(r"Window\s+#\d+\s+Window\{[a-f0-9]+\s+u\d+\s+([\w\.]+)/", window_dump)
                if window_match:
                    apps_to_kill.add(window_match.group(1).strip())

        # Get all apps with active or cached media sessions
        sessions_output = self.device.shell("cmd media_session list-sessions")
        if sessions_output:
            packages = re.findall(r"package=(\S+)", sessions_output)
            for pkg in packages:
                apps_to_kill.add(pkg.strip())

        # Filter out core Android TV system components
        system_packages = {
            "android",
            "com.google.android.tvlauncher",
            "com.google.android.apps.tv.launcherx",
            "com.android.systemui"
        }
        apps_to_kill = apps_to_kill - system_packages

        # Terminate the active apps
        if not apps_to_kill:
            log.info("No active media or foreground apps found to reset.")
            self.Home()
            return True

        log.info(f"Active apps targeted for termination: {list(apps_to_kill)}")

        for app in apps_to_kill:
            cmd = f"am force-stop {app}"
            resp = self.device.shell(cmd)
            log.info(f"{cmd} executed. Response: {resp.strip() if resp else 'Success'}")
            self.sleep(1)

        # Return to clean Home screen state
        self.Home()
        self.sleep(2)
        return True

    def ResetOld(self):
        apps_to_kill = set()

        # Get the app physically in the foreground
        window_dump = self.device.shell("dumpsys window windows")
        if window_dump:
            focus_match = re.search(r"(?:mCurrentFocus|mFocusedApp)=Window\{[a-f0-9]+\s+u\d+\s+([\w\.]+)/", window_dump)
            if not focus_match:
                focus_match = re.search(r"mFocusedApp=ActivityRecord\{[a-f0-9]+\s+u\d+\s+([\w\.]+)/", window_dump)
            if focus_match:
                apps_to_kill.add(focus_match.group(1).strip())

        # Get all apps with active or cached media sessions
        sessions_output = self.device.shell("cmd media_session list-sessions")
        if sessions_output:
            # Find every package instance listed in the active sessions
            packages = re.findall(r"package=(\S+)", sessions_output)
            for pkg in packages:
                apps_to_kill.add(pkg.strip())

        # Filter out core Android TV system components to prevent
        # bootloops/UI crashes
        system_packages = {
            "android",
            "com.google.android.tvlauncher",
            "com.google.android.apps.tv.launcherx", # Google TV interface
            "com.android.systemui"
        }
        apps_to_kill = apps_to_kill - system_packages

        # Terminate the active apps
        if not apps_to_kill:
            log.info("No active media or foreground apps found to reset.")
            self.Home()
            return True

        log.info(f"Active apps targeted for termination: {list(apps_to_kill)}")

        for app in apps_to_kill:
            cmd = f"am force-stop {app}"
            resp = self.device.shell(cmd)
            # am force-stop usually outputs nothing on success, so we print the action
            log.info(f"{cmd} executed. Response: {resp.strip() if resp else 'Success'}")
            self.sleep(1)

        # Return to clean Home screen state
        self.Home()
        self.sleep(2)
        return True

    def WakeUp(self):
        self.Wakeup()
        self.Reset()

    def MediaState(self, val = None, args = None):
        ACTIONS = {
            0x00000001: "STOP",
            0x00000002: "PAUSE",
            0x00000004: "PLAY",
            0x00000008: "REWIND",
            0x00000010: "PREVIOUS",
            0x00000020: "NEXT",
            0x00000040: "FAST_FORWARD",
            0x00000080: "SET_RATING",
            0x00000100: "SEEK_TO",
            0x00000200: "PLAY_PAUSE",
            0x00000400: "PLAY_FROM_MEDIA_ID",
            0x00000800: "PLAY_FROM_SEARCH",
            0x00001000: "SKIP_TO_QUEUE_ITEM",
            0x00002000: "PLAY_FROM_URI",
            0x00004000: "PREPARE",
            0x00008000: "PREPARE_FROM_MEDIA_ID",
            0x00010000: "PREPARE_FROM_SEARCH",
            0x00020000: "PREPARE_FROM_URI",
            0x00040000: "SET_REPEAT_MODE",
            0x00080000: "SET_SHUFFLE_MODE_ENABLED",
            0x00100000: "SET_CAPTIONING_ENABLED",
            0x00200000: "SET_SHUFFLE_MODE",
            0x00400000: "SET_PLAYBACK_SPEED",
        }

        cmd = 'dumpsys media_session'

        try:
            resp = self.device.shell(cmd)

            playback_line = ""
            for line in resp.splitlines():
                if "state=PlaybackState" in line:
                    playback_line = line
                    break
            else:
#                {"is_landing_page": True, "playback_state": "stopped",
#                        "error": "No active media session"}
                return "UNKNOWN"

            state_match = re.search(r'actions=(\d+)', playback_line)
            mask = int(state_match.group(1))
            states_str = [name for bit, name in ACTIONS.items() if mask & bit]

            log.info(f"{playback_line}\n{states_str}")

            # state=PlaybackState {state=PLAYING(3), position=546849
            # state=PlaybackState {state=PAUSED(2), position=845739

            # Extract position via regex (looks for 'position=12345')
            pos_match = re.search(r'position=(\d+)', playback_line)
            if not pos_match:
#                return {"is_landing_page": True, "playback_state": "unknown",
#                        "error": "Could not parse position value"}
                return "IDLE"

            position_val = int(pos_match.group(1))

            # This matches '{state=PAUSED(2)' or '{state=3' while ignoring
            # the initial 'state=PlaybackState'
            state_match = re.search(r'\{state=(?:([A-Z_]+)\()?(\d+)?',
                                    playback_line)

            state = "UNKNOWN"
            if state_match:
                state_name = state_match.group(1)  # e.g., "PLAYING" or "PAUSED"
                state_code = state_match.group(2)  # e.g., "3" or "2"

                if state_name:
                    state = state_name.upper()
                elif state_code:
                    # Fallback mapping if only integers are present
                    mapping = {"3": "PLAYING", "2": "PAUSED"}
                    state = mapping.get(state_code, "UNKNOWN")
            else:
                state = "UNKNOWN"

            if position_val < 1000: # ms
                state = "IDLE"

        except Exception as e:
            log.exception(e)
            state = "UNKNOWN"

        return state

    def parse_link(self, link):
        parts = link.split('/')
        if len(parts[1]) > 0:
            category = parts[1]
            link = parts[0] + '//' + '/'.join(parts[2:])
        else:
            category = None
        return link, category

    @register_handler('link', 'victory')
    def victory_link(self, link):
#adb shell am start -a android.intent.action.VIEW -n tv.apmc.android.victorysports/tv.kidoodle.android.ui.MainActivity
        link, category = self.parse_link(link)
        app = "tv.apmc.android.victorysports/tv.kidoodle.android.ui.MainActivity"
        nav_keys = f'wait 10 select wait 2'
        link = None
        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}


    @register_handler('link', 'nwsl')
    @register_handler('link', 'www.nwslsoccer.com')
    @register_handler('link', 'plus.nwslsoccer.com')
    def nwsl_link(self, link):
        # https://www.nwslsoccer.com/match/98c13cd2f1554ce0ba2aca6de0766735/north-carolina-courage-vs-seattle-reign

        app = "com.nwsl.plus/.MainActivity"

        show_id = link
        search = show_id.split('/')[-1] if '/' in show_id else show_id
        # Make sure we are "home" within the app
        nav_keys = 'left 6 wait 1 left up 4 down 1 select wait 5'
        # Move to search
        nav_keys += ' left wait 1 down 4 up 1 select wait 2 select wait 2 '
        # Search for match
        nav_keys += f' string "{search}" wait 2 down 4 select '
        # Limit results to Live
        nav_keys += ' wait 2 down right select wait 2 right select wait 2 select wait 2 back wait 2 back '
        # Now select first (hopefully correct) episode
        nav_keys += ' wait 2 down wait 2 select '

        link_type = 'live'
        link = None
        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}


    @register_handler('link', 'youtubetv')
    @register_handler('link', 'tv.youtube.com')
    def yttv_link(self, link):
#        if self.device_name == 'cube':
        link, category = self.parse_link(link)

        app = "com.google.android.youtube.tvunplugged"
        nav_keys = "wait 10"
        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}

    @register_handler('link', 'www.disneyplus.com')
    def disney_link(self, link):
# adb shell am start -a android.intent.action.VIEW -d "https://www.disneyplus.com/play/2bd7eb2e-6a06-4ba8-a057-5e941d5400f1" com.disney.disneyplus

        link, category = self.parse_link(link)
        app = "com.disney.disneyplus"
        nav_keys = "select wait 15 select wait 5"
        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}

    @register_handler('link', 'www.paramountplus.com')
    def paramount_link(self, link):
# adb shell am start -a android.intent.action.VIEW -d "https://www.paramountplus.com/shows/video/024nWQfVtByAvsmL1X4cFvAFXYmZC2kr/" com.cbs.cbsnews

        link, category = self.parse_link(link)
        app = 'com.cbs.ott'
        nav_keys = 'wait 7'
        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}

    @register_handler('link', 'aiv')
    @register_handler('link', 'www.amazon.com')
    def amazon_link(self, link):
# adb shell am start -a android.intent.action.VIEW -d aiv://watch/asin=B0GZ39BDJS -n com.amazon.amazonvideo.livingroom/com.amazon.ignition.IgnitionActivity
        link, category = self.parse_link(link)
        link = link.replace('://', '://watch/asin=')

        if self.device_name.startswith('cube'):
            app = ''
            nav_keys = ''
        else:
            app = 'com.amazon.amazonvideo.livingroom/com.amazon.ignition.IgnitionActivity'
            nav_keys = 'wait 9 select wait 5 select wait 5'

        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}


    @register_handler('link', 'www.pbs.org')
    def pbs_link(self, link):
# adb shell am start -a android.intent.action.VIEW -d "https://www.pbs.org/video/the-american-revolution-the-revolution-that-changed-the-world-bj1hwy/" org.pbs.video

        link, category = self.parse_link(link)
        app = '' # org.pbs.video'  # works without specifying app
        nav_keys = 'wait 7'
        return {'app'      : app,
                'activity' : None,
                'link'     : link,
                'keys'     : nav_keys}


    def LaunchLink(self, service, link, content_type):
        if service not in self.link_handlers:
            log.error(f"Failed to find deep link method for {service}")
            return None
        handler = self.link_handlers[service]
        params = handler(link)
        if params is None:
            return None

        self.Reset()

        if params['link'] is None:
            cmd = (f"am start -a android.intent.action.VIEW -n {params['app']}"
                   ' --es "categorySlug" "Utah Royals vs Gotham FC"')

        elif params['activity'] is None:
            cmd = f"am start -a android.intent.action.VIEW -d {params['link']} {params['app']}"
        else:
            cmd = f"am start -a android.intent.action.VIEW -d {params['link']} -n {params['app']}/{params['activity']}"
        log.info(f"Launching {cmd}")
        self.device.shell(cmd)

        return params['keys']

    @register_handler('prologue', 'amazon')
    def amazon_prologue(self):
        return ' wait 60 '

    @register_handler('epilogue', 'amazon')
    def amazon_epilogue(self):
        return 'up 3 wait 0.25 select wait 1'

    @register_handler('prologue', 'disney')
    def disney_prologue(self):
        return ' wait 15 '

    @register_handler('epilogue', 'disney')
    def disney_epilogue(self):
        return 'up 3 wait 0.25 select wait 0.75'

    def Prologue(self, service, args = None):
        log.info(f"Prologue {service}")
        prologue = self.prologue_handlers.get(service)
        if prologue:
            try:
                log.info(f"Executing prologue for {service}...")
                return self.Keys(prologue())
            except Exception as e:
                log.error(f"Error running prologue for {service}: {e}")
        return False

    def Epilogue(self, service, args = None):
        log.info(f"Epilogue {service}")
        epilogue = self.epilogue_handlers.get(service)
        if epilogue:
            try:
                log.info(f"Executing epilogue for {service}...")
                return self.Keys(epilogue())
            except Exception as e:
                log.error(f"Error running epilogue for {service}: {e}")
        return False
