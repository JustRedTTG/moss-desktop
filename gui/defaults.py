import os.path
import sys
import __main__

try:
    from cefpython3 import cefpython as cef
except Exception:
    cef = None
import pygameextra as pe


def get_asset_path():
    # Check if we are running in a Nuitka bundle
    if compiled := globals().get('__compiled__'):
        asset_dir = os.path.join(compiled.containing_dir, 'assets')
        script_dir = os.path.abspath(os.path.dirname(sys.executable))
    else:
        asset_dir = os.path.join(os.path.abspath("."), 'assets')
        script_dir = os.path.abspath(os.path.dirname(__main__.__file__))
    return asset_dir, script_dir


class Defaults:
    ASSET_DIR, SCRIPT_DIR = get_asset_path()

    HTML_DIR = os.path.join(ASSET_DIR, 'html')
    ICON_DIR = os.path.join(ASSET_DIR, 'icons')
    FONT_DIR = os.path.join(ASSET_DIR, 'fonts')

    TOKEN_FILE_PATH = os.path.join(SCRIPT_DIR, 'token')
    SYNC_FILE_PATH = os.path.join(SCRIPT_DIR, 'sync')

    CUSTOM_FONT = os.path.join(FONT_DIR, 'Imperator.ttf')
    CUSTOM_FONT_BOLD = os.path.join(FONT_DIR, 'Imperator Bold.ttf')
    MONO_FONT = os.path.join(FONT_DIR, 'JetBrainsMono-Bold.ttf')
    FOLDER_FONT = os.path.join(FONT_DIR, 'Roboto-Medium.ttf')
    PATH_FONT = os.path.join(FONT_DIR, 'Roboto-Regular.ttf')
    DOCUMENT_TITLE_FONT = os.path.join(FONT_DIR, 'Roboto-Regular.ttf')
    DOCUMENT_ERROR_FONT = os.path.join(FONT_DIR, 'Roboto-Medium.ttf')

    LOGO_FONT = CUSTOM_FONT_BOLD
    MAIN_MENU_FONT = CUSTOM_FONT_BOLD
    CODE_FONT = MONO_FONT
    DEBUG_FONT = MONO_FONT

    TEXT_COLOR = (pe.colors.black, pe.colors.white)
    DOCUMENT_TITLE_COLOR = ((20, 20, 20), TEXT_COLOR[1])
    DOCUMENT_SUBTITLE_COLOR = ((100, 100, 100), TEXT_COLOR[1])
    TEXT_COLOR_T = (TEXT_COLOR[0], None)
    TEXT_COLOR_H = (TEXT_COLOR[1], None)
    CODE_COLOR = ((120, 120, 120), None)
    LINE_GRAY = (88, 88, 88)
    DOCUMENT_GRAY = (184, 184, 184)
    TRANSPARENT_COLOR = (0, 0, 0, 0)
    BUTTON_ACTIVE_COLOR = (0, 0, 0, 25)

    # Colors
    RED = (255, 50, 50)

    # Key bindings
    NAVIGATION_KEYS = {
        "next": [pe.K_RIGHT],
        "previous": [pe.K_LEFT],
    }
