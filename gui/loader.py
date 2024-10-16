import os
import threading
import time
from logging import lastResort

import pygameextra as pe
from typing import TYPE_CHECKING

from .defaults import Defaults
from .main_menu import MainMenu

if TYPE_CHECKING:
    from .gui import GUI


class Loader(pe.ChildContext):
    TO_LOAD = {
        'folder': os.path.join(Defaults.ICON_DIR, 'folder.svg'),
        'folder_inverted': os.path.join(Defaults.ICON_DIR, 'folder_inverted.svg'),
        'chevron_right': os.path.join(Defaults.ICON_DIR, 'chevron_right.svg'),
        'chevron_down': os.path.join(Defaults.ICON_DIR, 'chevron_down.svg'),
        #'screenshot': 'screenshot_for_reference2.png',
    }
    LAYER = pe.AFTER_LOOP_LAYER

    def __init__(self, parent: 'GUI'):
        super().__init__(parent)
        self.logo = pe.Text(
            "RedTTG",
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
        self.files_to_load = 999
        self.last_progress = 0
        self.current_progress = 0
        threading.Thread(target=self.load).start()
        threading.Thread(target=self.get_documents).start()

    def load(self):
        for key, item in self.TO_LOAD.items():
            if item.endswith('.svg'):
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

        self.api.get_documents(progress)

    def load_image(self, key, file, multiplier: float = 1):
        self.icons[key] = pe.Image(file)
        self.icons[key].resize(tuple(self.ratios.pixel(v*multiplier) for v in self.icons[key].size))

    def progress(self):
        try:
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
        return self.last_progress

    def loop(self):
        self.logo.display()
        pe.draw.rect(pe.colors.black, self.line_rect, 1)
        progress_rect = self.line_rect.copy()
        progress_rect.width *= self.progress()
        pe.draw.rect(pe.colors.black, progress_rect, 0)

    def post_loop(self):
        if self.current_progress == 1 and self.last_progress > .95:
            self.screens.put(MainMenu(self.parent_context))
