from typing import TYPE_CHECKING, Dict
import pygameextra as pe

from gui.defaults import Defaults
from gui.pp_helpers import FullTextPopup
from gui.viewer import DocumentViewer

if TYPE_CHECKING:
    from gui import GUI
    from rm_api.models import DocumentCollection
    from rm_api.models import Document
    from queue import Queue


def render_collection(gui: 'GUI', collection: 'DocumentCollection', text: pe.Text, callback, x, y):
    icon = gui.icons['folder_inverted']
    icon.display((x, y))
    text.rect.midleft = (x, y)
    text.rect.x += icon.width + gui.ratios.main_menu_folder_padding
    text.rect.y += icon.height // 1.5
    text.display()
    rect = pe.rect.Rect(
        x, y,
        gui.ratios.main_menu_document_width -
        gui.ratios.main_menu_folder_padding,
        icon.height
    )
    rect.inflate_ip(gui.ratios.main_menu_folder_margin_x, gui.ratios.main_menu_folder_margin_y)
    pe.button.rect(
        rect,
        Defaults.TRANSPARENT_COLOR, Defaults.TRANSPARENT_COLOR,
        action=callback, data=collection.uuid,
        hover_draw_action=pe.draw.rect,
        hover_draw_data=(Defaults.LINE_GRAY, rect, gui.ratios.pixel(3))
    )


def render_full_document_title(gui: 'GUI', texts, document_uuid: str):
    text = texts[document_uuid]
    text_full = texts[document_uuid + '_full']
    if text.text != text_full.text:
        FullTextPopup.create(gui, text_full, text)()


def open_document(gui: 'GUI', document_uuid: str):
    gui.screens.put(DocumentViewer(gui, document_uuid))


def render_document(gui: 'GUI', rect: pe.Rect, texts, document: 'Document'):
    title_text = texts[document.uuid]

    title_text.rect.topleft = rect.bottomleft
    title_text.rect.top += gui.ratios.main_menu_document_title_height_margin

    action = document.ensure_download_and_callback
    data = lambda: open_document(gui, document.uuid)
    disabled = document.downloading

    render_button_using_text(
        gui, title_text,
        Defaults.TRANSPARENT_COLOR, Defaults.TRANSPARENT_COLOR,
        name=document.uuid + '_title_hover',
        hover_draw_action=render_full_document_title,
        hover_draw_data=(gui, texts, document.uuid),
        action=action,
        data=data,
        disabled=disabled
    )

    # Render the passive outline
    pe.draw.rect(
        Defaults.DOCUMENT_GRAY,
        rect, gui.ratios.pixel(2)
    )
    # Render the button
    pe.button.rect(
        rect,
        Defaults.TRANSPARENT_COLOR, Defaults.BUTTON_ACTIVE_COLOR,
        name=document.uuid,
        action=action,
        data=data,
        disabled=disabled
    )


def render_button_using_text(
        gui: 'GUI', text: pe.Text,
        inactive_color=Defaults.TRANSPARENT_COLOR, active_color=Defaults.BUTTON_ACTIVE_COLOR,
        *args,
        name: str = None, action=None, data=None,
        **kwargs
):
    text.display()
    pe.button.rect(
        gui.ratios.pad_button_rect(text.rect),
        inactive_color, active_color,
        *args,
        name=name,
        action=action,
        data=data,
        **kwargs
    )


def render_header(gui: 'GUI', texts: Dict[str, pe.Text], callback, path_queue: 'Queue'):
    render_button_using_text(gui, texts['my_files'], action=callback)

    x = texts['my_files'].rect.right + gui.ratios.main_menu_path_padding
    y = texts['my_files'].rect.centery

    width = 0
    skips = 0

    # Calculate the width of the path
    for item in path_queue.queue:
        text_key = f'path_{item}'
        width += gui.icons['chevron_right'].width + texts[text_key].rect.width

    # Calculate the number of items to skip in the path, this results in the > > you see in the beginning
    while width > gui.width - (x + 200):
        skips += 1
        width -= texts[f'path_{path_queue.queue[-skips]}'].rect.width

    # Draw the path
    for i, item in enumerate(reversed(path_queue.queue)):
        text_key = f'path_{item}'

        # Draw the arrow
        if i >= skips or i < 1:  # Making sure to render the arrow only for the first skip, making sure to avoid > > > >
            gui.icons['chevron_right'].display((x, y - gui.icons['chevron_right'].height // 2))

            x += gui.icons['chevron_right'].width
            if i == 0:
                x += gui.ratios.main_menu_path_first_padding

        # Draw the text only if it's not skipped
        if i >= skips:
            texts[text_key].rect.midleft = (x, y)
            render_button_using_text(gui, texts[text_key], action=callback, data=item)
            x += texts[text_key].rect.width
