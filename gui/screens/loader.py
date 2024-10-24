import os
import threading

import pygameextra as pe
from typing import TYPE_CHECKING, Union, Dict

from rm_api.notifications.models import SyncCompleted
from gui.defaults import Defaults
from gui.screens.main_menu import MainMenu

from gui.gui import APP_NAME

if TYPE_CHECKING:
    from gui.gui import GUI
    from rm_api import API


class ReusedIcon:
    def __init__(self, key: str, scale: float):
        self.key = key
        self.scale = scale


class Loader(pe.ChildContext):
    TO_LOAD = {
        'folder': os.path.join(Defaults.ICON_DIR, 'folder.svg'),
        'folder_inverted': os.path.join(Defaults.ICON_DIR, 'folder_inverted.svg'),
        'chevron_right': os.path.join(Defaults.ICON_DIR, 'chevron_right.svg'),
        'chevron_down': os.path.join(Defaults.ICON_DIR, 'chevron_down.svg'),
        'cloud': os.path.join(Defaults.ICON_DIR, 'cloud.svg'),
        'cloud_download': os.path.join(Defaults.ICON_DIR, 'cloud_download.svg'),
        'warning_circle': os.path.join(Defaults.ICON_DIR, 'warning_circle.svg'),
        'notebook': os.path.join(Defaults.ICON_DIR, 'notebook.svg'),
        'notebook_large': os.path.join(Defaults.ICON_DIR, 'notebook_large.svg'),
        # 'screenshot': 'screenshot_for_reference2.png',
    }

    LAYER = pe.AFTER_LOOP_LAYER
    icons: Dict[str, pe.Image]
    api: 'API'

    def __init__(self, parent: 'GUI'):
        super().__init__(parent)
        self.logo = pe.Text(
            APP_NAME,
            Defaults.LOGO_FONT, self.ratios.loader_logo_text_size,
            pe.math.center(
                (
                    0, 0, self.width,
                    self.height - (
                            self.ratios.loader_loading_bar_height + self.ratios.loader_loading_bar_padding
                    )
                )
            ),
            Defaults.TEXT_COLOR
        )
        self.line_rect = pe.Rect(0, 0, self.ratios.loader_loading_bar_width,
                                 self.ratios.loader_loading_bar_height)
        self.line_rect.midtop = self.logo.rect.midbottom
        self.line_rect.top += self.ratios.loader_loading_bar_padding
        self.items_loaded = 0
        self.files_loaded = 0
        self.loading_feedback = 0  # Used by main menu to know if enough changes have been made since last checked
        self.files_to_load: Union[int, None] = None
        self.last_progress = 0
        self.current_progress = 0
        self.initialized = False

    def start_syncing(self):
        threading.Thread(target=self.get_documents, daemon=False).start()

    def load(self):
        for key, item in self.TO_LOAD.items():
            if isinstance(item, ReusedIcon):
                self.icons[key] = self.icons[item.key].copy()
                self.icons[key].resize(tuple(v * item.scale for v in self.icons[key].size))
            elif not isinstance(item, str):
                continue
            elif item.endswith('.svg'):
                # SVGs are 40px, but we use 1000px height, so they are 23px
                # 23 / 40 = 0.575
                # but, I find 0.5 to better match
                self.load_image(key, item, 0.5)
            elif item.endswith('.png'):
                self.load_image(key, item)
            self.items_loaded += 1

    def get_documents(self):
        def progress(loaded, to_load):
            self.files_loaded = loaded
            self.files_to_load = to_load

        self.loading_feedback = 0
        self.api.get_documents(progress)
        self.files_to_load = None

    def load_image(self, key, file, multiplier: float = 1):
        self.icons[key] = pe.Image(file)
        self.icons[key].resize(tuple(self.ratios.pixel(v * multiplier) for v in self.icons[key].size))

    def progress(self):
        if self.files_to_load is None and self.config.wait_for_everything_to_load and not self.current_progress:
            # Before we know the file count, just return 0 progress
            return 0
        try:
            if not self.files_to_load or not self.config.wait_for_everything_to_load:
                self.current_progress = self.items_loaded / len(self.TO_LOAD)
            else:
                self.current_progress = (
                                                self.items_loaded +
                                                self.files_loaded
                                        ) / (
                                                len(self.TO_LOAD) +
                                                self.files_to_load
                                        )
        except ZeroDivisionError:
            self.current_progress = 0
        self.last_progress = self.last_progress + (self.current_progress - self.last_progress) / (self.FPS * .1)
        if self.last_progress > .98:
            self.last_progress = 1
        return self.last_progress

    def loop(self):
        self.logo.display()
        pe.draw.rect(pe.colors.black, self.line_rect, 1)
        progress_rect = self.line_rect.copy()
        progress_rect.width *= self.progress()
        pe.draw.rect(pe.colors.black, progress_rect, 0)

    def post_loop(self):
        if self.current_progress == 1 and self.last_progress == 1:
            self.screens.put(MainMenu(self.parent_context))
            self.api.connect_to_notifications()
            self.api.add_hook('loader', self.loader_hook)

    def loader_hook(self, event):
        if isinstance(event, SyncCompleted):
            self.start_syncing()

    def pre_loop(self):
        if not self.initialized:
            threading.Thread(target=self.load, daemon=True).start()
            self.start_syncing()
            self.initialized = True
