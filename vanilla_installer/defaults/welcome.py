# welcome.py
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

import sys
import time
from gi.repository import Gtk, Gio, GLib, Adw

from vanilla_installer.windows.dialog_poweroff import VanillaPoweroffDialog

@Gtk.Template(resource_path='/org/vanillaos/Installer/gtk/default-welcome.ui')
class VanillaDefaultWelcome(Adw.Bin):
    __gtype_name__ = 'VanillaDefaultWelcome'

    btn_live = Gtk.Template.Child()
    btn_poweroff = Gtk.Template.Child()
    btn_next = Gtk.Template.Child()

    def __init__(self, window, distro_info, key, step, **kwargs):
        super().__init__(**kwargs)
        self.__window = window
        self.__distro_info = distro_info
        self.__key = key
        self.__step = step

        # signals
        self.btn_next.connect("clicked", self.__window.next)
        self.btn_live.connect('clicked', self.__on_live_clicked)
        self.btn_poweroff.connect('clicked', self.__on_recovery_clicked)

    def get_finals(self):
        return {}
    
    def __on_live_clicked(self, button):
        def close_window(_widget, response_id):
            if response_id == "try":
                _widget.destroy()
                self.__window.destroy()
            elif response_id == "cancel":
                _widget.destroy()

        dialog = Adw.MessageDialog()
        dialog.set_transient_for(self.__window)
        dialog.set_size_request(400, -1)
        dialog.set_heading("Try zarya")
        dialog.set_body("Use zarya in live session without installing.")
        dialog.add_response("cancel", _("_Cancel"))
        dialog.add_response("try", _("Try zarya"))
        dialog.connect("response", close_window)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.present()

    def __on_recovery_clicked(self, button):
        VanillaPoweroffDialog(self.__window).show()
        
