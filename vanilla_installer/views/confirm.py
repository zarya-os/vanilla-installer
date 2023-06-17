# dialog.py
#
# Copyright 2022 mirkobrombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundationat version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GObject, Adw
from gettext import gettext as _

@Gtk.Template(resource_path='/org/vanillaos/Installer/gtk/widget-choice.ui')
class VanillaChoiceEntry(Adw.ActionRow):
    __gtype_name__ = 'VanillaChoiceEntry'

    img_choice = Gtk.Template.Child()

    def __init__(self, title, subtitle,icon_name, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.img_choice.set_from_icon_name(icon_name)


@Gtk.Template(resource_path='/org/vanillaos/Installer/gtk/widget-choice-expander.ui')
class VanillaChoiceExpanderEntry(Adw.ExpanderRow):
    __gtype_name__ = 'VanillaChoiceExpanderEntry'

    img_choice = Gtk.Template.Child()

    def __init__(self, title, subtitle,icon_name, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.img_choice.set_from_icon_name(icon_name)


@Gtk.Template(resource_path='/org/vanillaos/Installer/gtk/confirm.ui')
class VanillaConfirm(Adw.Bin):
    __gtype_name__ = 'VanillaConfirm'
    __gsignals__ = {
        "installation-confirmed": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    group_changes = Gtk.Template.Child()
    btn_confirm = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
    
    def update(self, finals):
        try:
            for widget in self.active_widgets:
                self.group_changes.remove(widget)
        except AttributeError:
            pass
        self.active_widgets = []

        for final in finals:
            for key, value in final.items():

                if key == "language":
                    self.active_widgets.append(VanillaChoiceEntry(
                        _("Language"),
                        value,
                        "preferences-desktop-locale-symbolic"
                    ))
                elif key == "keyboard":
                    self.active_widgets.append(VanillaChoiceEntry(
                        _("Keyboard"),
                        value,
                        "input-keyboard-symbolic"
                    ))
                elif key == "disk":
                    if "auto" in value:
                        self.active_widgets.append(VanillaChoiceEntry(
                            _("Disk"),
                            f"{value['auto']['disk']} ({value['auto']['pretty_size']})",
                            "drive-harddisk-system-symbolic"
                        ))
                    else:
                        i = 0
                        for block, block_info in value.items():
                            if i == 0:
                                expander = VanillaChoiceExpanderEntry(
                                    _("Disk"),
                                    block_info,
                                    "drive-harddisk-system-symbolic"
                                )
                                self.active_widgets.append(expander)
                            else:
                                expander.add_row(VanillaChoiceEntry(
                                    block,
                                    f"{block_info['fs']} {block_info['mp']} ({block_info['pretty_size']})",
                                    "drive-harddisk-system-symbolic"
                                ))
                            i += 1

        for widget in self.active_widgets:
            self.group_changes.add(widget)

        self.btn_confirm.connect(_("clicked"), self.__on_confirm)

    def __on_confirm(self, widget):
        self.emit(_("installation-confirmed"))
