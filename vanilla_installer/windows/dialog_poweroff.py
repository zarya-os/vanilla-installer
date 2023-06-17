# dialog_recovery.py
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

import subprocess
from gi.repository import Gtk, GLib, Adw
from gettext import gettext as _

from vanilla_installer.core.system import Systeminfo


@Gtk.Template(resource_path='/org/vanillaos/Installer/gtk/dialog-poweroff.ui')
class VanillaPoweroffDialog(Adw.Window):
    __gtype_name__ = 'VanillaPoweroffDialog'

    btn_poweroff = Gtk.Template.Child()
    btn_restart = Gtk.Template.Child()
    btn_firmware_setup = Gtk.Template.Child()
    btn_firmware_row = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(window)
        # signals
        self.btn_poweroff.connect('clicked', self.__on_poweroff)
        self.btn_restart.connect('clicked', self.__on_restart)
        self.btn_firmware_setup.connect('clicked', self.__on_firmware_setup)

        self.btn_firmware_setup.set_visible(Systeminfo.is_uefi())
        self.btn_firmware_row.set_visible(Systeminfo.is_uefi())

    def __show_dialog(self, title, body, option_label, option_cmd):
        def dialog_response_callback(dialog, response_id):
            if response_id == 'yes':
                subprocess.call(option_cmd.split())
            dialog.destroy()

        dialog = Adw.MessageDialog()
        dialog.set_transient_for(self)
        dialog.set_size_request(400, -1)
        dialog.set_heading(title)
        dialog.set_body(body)
        dialog.add_response('cancel', _("_Cancel"))
        dialog.add_response('yes', option_label)
        dialog.connect("response", dialog_response_callback)
        dialog.set_default_response('cancel')
        dialog.set_close_response('cancel')
        dialog.present()

    def __on_poweroff(self, button):
        title = "Power Off"
        body = "The system will power off."
        option_label = _("Power Off")
        option_cmd = "systemctl poweroff"
        self.__show_dialog(title, body, option_label, option_cmd)

    def __on_restart(self, button):
        title = "Restart"
        body = "The system will restart."
        option_label = _("_Restart")
        option_cmd = "systemctl reboot"
        self.__show_dialog(title, body, option_label, option_cmd)

    def __on_firmware_setup(self, button):
        title = "Firmware setup"
        body = "The system will restart into firmware setup."
        option_label = _("_Restart")
        option_cmd = "systemctl reboot --firmware-setup"
        self.__show_dialog(title, body, option_label, option_cmd)
