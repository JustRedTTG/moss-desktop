import gui
from gui.gui import GUI
from melora import melora_patch
from melora.injector import Injector

_gui = GUI()
melora_patch()
_injector = Injector(_gui)

while _gui.running:
    _injector.run_pp_helpers()
    _gui()

print("Saving melora extensions")
for extension in _injector.extensions.values():
    extension.save()
_gui.save_config_if_dirty()
