# processor.py
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

import os
import uuid
import shutil
import logging
import tempfile
import subprocess
from glob import glob
import re
import json

from gettext import gettext as _
from vanilla_installer.core.system import Systeminfo

logger = logging.getLogger("Installer::Processor")


class Processor:
    
    @staticmethod
    def gen_install_script(log_path, pre_run, post_run, finals):
        logger.info("processing the following final data: %s", finals)

        # manifest_remove = "/cdrom/casper/filesystem.manifest-remove"
        # if not os.path.exists(manifest_remove):
        manifest_remove = "/tmp/filesystem.manifest-remove"
        with open(manifest_remove, "w") as f:
            f.write("gparted\n")

        arguments = [
            "sudo",
            "distinst",
            "--run-ubuntu-drivers",
            "-s",
            "'/cdrom/casper/filesystem.squashfs'",
            "-r",
            f"'{manifest_remove}'",
            "-h",
            "'zarya'",
        ]

        # post install variables
        device_block = ""
        finals_disk = {}

        for final in finals:
            for key, value in final.items():
                if key == "language":
                    arguments += ["-l", f"'{value}'"]
                elif key == "keyboard":
                    arguments += ["-k", f"'{value}'"]
                elif key == "disk":
                    finals_disk = final
                    if "auto" in value:
                        device_block = value["auto"]["disk"]
                        arguments += ["-b", f"'{device_block}'"]
                        if Systeminfo.is_uefi():
                            arguments += ["-t", f"'{device_block}:gpt'"]
                            arguments += [
                            "-n",
                            f"'{device_block}:primary:start:1024M:fat32:mount=/boot/efi:flags=esp'",
                            ]
                            arguments += [
                            "-n",
                            f"'{device_block}:primary:1024M:end:ext4:mount=/'",
                            ]
                            # Add generated partitions to finals so abroot-adapter can find them
                            finals_disk["disk"]["disk"] = device_block
                            if not re.match(r"[0-9]", device_block[-1]):
                                partition_name = f"{device_block}"
                            else:
                                partition_name = f"{device_block}p"
                            finals_disk["disk"][f"{partition_name}1"] = {
                                "fs": "fat32",
                                "mp": "/boot/efi",
                            }
                            finals_disk["disk"][f"{partition_name}2"] = {
                                "fs": "ext4",
                                "mp": "/",
                            }
                        else:
                            arguments += ["-t", f"'{device_block}:msdos'"]
                            arguments += [
                                "-n",
                                f"'{device_block}:primary:start:end:ext4:mount=/'",
                            ]
                            # Add generated partitions to finals so abroot-adapter can find them
                            finals_disk["disk"]["disk"] = device_block
                            if not re.match(r"[0-9]", device_block[-1]):
                                partition_name = f"{device_block}"
                            else:
                                partition_name = f"{device_block}p"
                            finals_disk["disk"][f"{partition_name}1"] = {
                                "fs": "ext4",
                                "mp": "/",
                            }
                    else:
                        device_block = value["disk"]
                        for partition, values in value.items():
                            if partition == "disk":
                                arguments += ["-b", f"'{values}'"]
                                continue

                            partition_number = re.sub(r".*[a-z]([0-9]+)", r"\1", partition)
                            if values["mp"] == "/boot/efi":
                                arguments += [
                                    "-u",
                                    "'{}:{}:{}:mount=/boot/efi:flags=esp'".format(
                                        device_block, partition_number, values["fs"]
                                    ),
                                ]
                            elif values["mp"] == "swap":
                                arguments += [
                                    "-u",
                                    f"'{device_block}:{partition_number}:swap'",
                                ]
                            else:
                                arguments += [
                                    "-u",
                                    "'{}:{}:{}:mount={}'".format(
                                        device_block,
                                        partition_number,
                                        values["fs"],
                                        values["mp"],
                                    ),
                                ]

        # generating a temporary file to store the distinst command and
        # arguments parsed from the final data
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("#!/bin/sh\n")
            f.write("# This file was created by the Vanilla Installer.\n")
            f.write("# Do not edit this file manually!\n\n")

            f.write("set -e -x\n\n")

            if "VANILLA_FAKE" in os.environ:
                logger.info("VANILLA_FAKE is set, skipping the installation process.")
                f.write(
                    "echo 'VANILLA_FAKE is set, skipping the installation process.'\n"
                )
                f.write("echo 'Printing the configuration instead:'\n")
                f.write("echo '----------------------------------'\n")
                f.write(f'echo "{finals}"\n')
                f.write("echo '----------------------------------'\n")
                f.write("sleep 5\n")
                f.write("exit 1\n")

            if "VANILLA_SKIP_INSTALL" not in os.environ:
                for arg in arguments:
                    f.write(arg + " ")

            f.flush()
            f.close()

            # setting the file executable
            os.chmod(f.name, 0o755)

            return f.name
