from functools import lru_cache

from .common import INJECTOR_COLOR
from gui import GUI
import pygameextra as pe


class InjectorMenu(pe.ChildContext):
    LAYER = pe.AFTER_LOOP_LAYER
    parent_context: GUI

    def __init__(self, injector: 'Injector'):
        self.injector = injector
        self.gui = injector.parent_context
        self.rect = None
        super().__init__(injector.parent_context)

    def pre_loop(self):
        self.rect = pe.Rect(0, 0, self.width // 2,
                            self.height - self.gui.ratios.bottom_bar_height - self.gui.ratios.main_menu_top_height)
        self.rect.right = self.width + self.width * (1 - self.injector.t)
        self.rect.top += self.height * (1 - self.injector.t)
        self.rect.top += self.gui.ratios.main_menu_top_height
        pe.button.action(self.rect, name='injector_menu')
        pe.draw.rect(INJECTOR_COLOR, self.rect)

    @property
    def defaults(self):
        from gui.defaults import Defaults
        return Defaults

    @lru_cache
    def get_text(self, text):
        return pe.Text(text, self.defaults.MONO_FONT, self.gui.ratios.pixel(20), colors=self.defaults.TEXT_COLOR_T)

    def loop(self):
        from gui.rendering import render_button_using_text
        y = int(self.rect.top)
        button_height = self.gui.ratios.bottom_bar_height  # Just using the bottom bar height here
        for extension_id, extension in self.injector.extensions.items():
            for action_name, action_function in extension.ACTIONS.items():
                text = self.get_text(f'{extension.SHORT}: {action_name}')

                pe.button.rect(
                    (self.rect.x, y, self.rect.width, button_height),
                    self.defaults.TRANSPARENT_COLOR, self.defaults.BUTTON_ACTIVE_COLOR,
                    text,
                    action=self.call_and_close,
                    data=getattr(extension, action_function),
                    name=f'{extension_id}_{action_name}'
                )
                y += button_height

    def call_and_close(self, function):
        function()
        self.injector.reset_hover()

    def post_loop(self):
        if self.rect.collidepoint(*pe.mouse.pos()):
            self.injector.hover_hold()
