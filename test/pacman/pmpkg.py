#  Copyright (c) 2006 by Aurelien Foret <orelien@chez.com>
#  Copyright (c) 2006-2016 Pacman Development Team <pacman-dev@archlinux.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from StringIO import StringIO
import tarfile

import util

class pmpkg(object):
    """Package object.

    Object holding data from an Arch Linux package.
    """

    def __init__(self, name, version = "1.0-1"):
        self.path = "" #the path of the generated package
        # desc
        self.name = name
        self.version = version
        self.desc = ""
        self.groups = []
        self.url = ""
        self.license = []
        self.arch = ""
        self.builddate = ""
        self.installdate = ""
        self.packager = ""
        self.size = 0
        self.csize = 0
        self.isize = 0
        self.reason = 0
        self.md5sum = ""      # sync only
        self.pgpsig = ""      # sync only
        self.replaces = []
        self.depends = []
        self.optdepends = []
        self.conflicts = []
        self.provides = []
        # files
        self.files = []
        self.backup = []
        # install
        self.install = {
            "pre_install": "",
            "post_install": "",
            "pre_remove": "",
            "post_remove": "",
            "pre_upgrade": "",
            "post_upgrade": "",
        }
        self.path = None
        self.finalized = False

    def __str__(self):
        s = [f"{self.fullname()}"]
        s.extend(
            (
                f"description: {self.desc}",
                f"url: {self.url}",
                f'files: {" ".join(self.files)}',
                "reason: %d" % self.reason,
            )
        )
        return "\n".join(s)

    def fullname(self):
        """Long name of a package.

        Returns a string formatted as follows: "pkgname-pkgver".
        """
        return f"{self.name}-{self.version}"

    def filename(self):
        """File name of a package, including its extension.

        Returns a string formatted as follows: "pkgname-pkgver.PKG_EXT_PKG".
        """
        return f"{self.fullname()}{util.PM_EXT_PKG}"

    @staticmethod
    def parse_filename(name):
        filename = name
        if filename[-1] == "*":
            filename = filename.rstrip("*")
        if filename.find(" -> ") != -1:
            filename, extra = filename.split(" -> ")
        elif filename.find("|") != -1:
            filename, extra = filename.split("|")
        return filename

    def makepkg(self, path):
        """Creates an Arch Linux package archive.

        A package archive is generated in the location 'path', based on the data
        from the object.
        """
        # .PKGINFO
        data = [
            f"pkgname = {self.name}",
            f"pkgver = {self.version}",
            f"pkgdesc = {self.desc}",
            f"url = {self.url}",
            f"builddate = {self.builddate}",
            f"packager = {self.packager}",
            f"size = {self.size}",
        ]
        if self.arch:
            data.append(f"arch = {self.arch}")
        data.extend(f"license = {i}" for i in self.license)
        data.extend(f"replaces = {i}" for i in self.replaces)
        data.extend(f"group = {i}" for i in self.groups)
        data.extend(f"depend = {i}" for i in self.depends)
        data.extend(f"optdepend = {i}" for i in self.optdepends)
        data.extend(f"conflict = {i}" for i in self.conflicts)
        data.extend(f"provides = {i}" for i in self.provides)
        data.extend(f"backup = {i}" for i in self.backup)
        archive_files = [(".PKGINFO", "\n".join(data))]
        # .INSTALL
        if any(self.install.values()):
            archive_files.append((".INSTALL", self.installfile()))

        self.path = os.path.join(path, self.filename())
        util.mkdir(os.path.dirname(self.path))

        # Generate package metadata
        tar = tarfile.open(self.path, "w:gz")
        for name, data in archive_files:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, StringIO(data))

        # Generate package file system
        for name in self.files:
            fileinfo = util.getfileinfo(name)
            info = tarfile.TarInfo(fileinfo["filename"])
            if fileinfo["hasperms"]:
                info.mode = fileinfo["perms"]
            elif fileinfo["isdir"]:
                info.mode = 0o755
            if fileinfo["isdir"]:
                info.type = tarfile.DIRTYPE
                tar.addfile(info)
            elif fileinfo["islink"]:
                info.type = tarfile.SYMTYPE
                info.linkname = fileinfo["link"]
                tar.addfile(info)
            else:
                # TODO wow what a hack, adding a newline to match mkfile?
                filedata = name + "\n"
                info.size = len(filedata)
                tar.addfile(info, StringIO(filedata))

        tar.close()

    def install_package(self, root):
        """Install the package in the given root."""
        for f in self.files:
            path = util.mkfile(root, f, f)
            if os.path.isfile(path):
                os.utime(path, (355, 355))

    def filelist(self):
        """Generate a list of package files."""
        return sorted([self.parse_filename(f) for f in self.files])

    def finalize(self):
        """Perform any necessary operations to ready the package for use."""
        if self.finalized:
            return

        # add missing parent dirs to file list
        # use bare file names so trailing ' -> ', '*', etc don't throw off the
        # checks for existing files
        file_names = self.filelist()
        for name in list(file_names):
            if os.path.isabs(name):
                raise ValueError(f"Absolute path in filelist '{name}'.")

            name = os.path.dirname(name.rstrip("/"))
            while name:
                if name in file_names:
                    # path exists as both a file and a directory
                    raise ValueError(f"Duplicate path in filelist '{name}'.")
                elif f"{name}/" in file_names:
                    # path was either manually included or already processed
                    break
                else:
                    file_names.append(f"{name}/")
                    self.files.append(f"{name}/")
                name = os.path.dirname(name)
        self.files.sort()

        self.finalized = True

    def local_backup_entries(self):
        return ["%s\t%s" % (self.parse_filename(i), util.mkmd5sum(i)) for i in self.backup]

    def installfile(self):
        data = [
            "%s() {\n%s\n}\n" % (key, value)
            for key, value in self.install.items()
            if value
        ]
        return "\n".join(data)

# vim: set ts=4 sw=4 et:
