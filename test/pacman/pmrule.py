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
import stat

import tap
import util

class pmrule(object):
    """Rule object
    """

    def __init__(self, rule):
        self.rule = rule
        self.false = 0
        self.result = 0

    def __str__(self):
        return self.rule

    def snapshots_needed(self):
        (testname, args) = self.rule.split("=")
        return [args] if testname in ["FILE_MODIFIED", "!FILE_MODIFIED"] else []

    def check(self, test):
        """
        """
        success = 1

        [testname, args] = self.rule.split("=")
        if testname[0] == "!":
            self.false = 1
            testname = testname[1:]
        [kind, case] = testname.split("_")
        [key, value] = args.split("|", 1) if "|" in args else [args, None]
        if kind == "PACMAN":
            if case == "RETCODE":
                if test.retcode != int(key):
                    success = 0
            elif case == "OUTPUT":
                logfile = os.path.join(test.root, util.LOGFILE)
                if not os.access(logfile, os.F_OK):
                    tap.diag("LOGFILE not found, cannot validate 'OUTPUT' rule")
                    success = 0
                elif not util.grep(logfile, key):
                    success = 0
            else:
                tap.diag(f"PACMAN rule '{case}' not found")
                success = -1
        elif kind == "PKG":
            localdb = test.db["local"]
            if newpkg := localdb.db_read(key):
                if case == "EXIST":
                    success = 1
                elif case == "VERSION":
                    if value != newpkg.version:
                        success = 0
                elif case == "DESC":
                    if value != newpkg.desc:
                        success = 0
                elif case == "GROUPS":
                    if value not in newpkg.groups:
                        success = 0
                elif case == "PROVIDES":
                    if value not in newpkg.provides:
                        success = 0
                elif case == "DEPENDS":
                    if value not in newpkg.depends:
                        success = 0
                elif case == "OPTDEPENDS":
                    success = next(
                        (
                            1
                            for optdep in newpkg.optdepends
                            if value == optdep.split(':', 1)[0]
                        ),
                        0,
                    )
                elif case == "REASON":
                    if newpkg.reason != int(value):
                        success = 0
                elif case == "FILES":
                    if value not in newpkg.files:
                        success = 0
                elif case == "BACKUP":
                    success = next((1 for f in newpkg.backup if f.startswith(value + "\t")), 0)
                else:
                    tap.diag(f"PKG rule '{case}' not found")
                    success = -1
            else:
                success = 0
        elif kind == "FILE":
            filename = os.path.join(test.root, key)
            if case == "EXIST":
                if not os.path.isfile(filename):
                    success = 0
            elif case == "EMPTY":
                if not os.path.isfile(filename) or os.path.getsize(filename) != 0:
                    success = 0
            elif case == "CONTENTS":
                try:
                    with open(filename, 'r') as f:
                        success = f.read() == value
                except:
                    success = 0
            elif case == "MODIFIED":
                for f in test.files:
                    if f.name == key:
                        if not f.ismodified():
                            success = 0
                        break
            elif case == "MODE":
                if not os.path.isfile(filename):
                    success = 0
                else:
                    mode = os.lstat(filename)[stat.ST_MODE]
                    if int(value, 8) != stat.S_IMODE(mode):
                        success = 0
            elif case == "TYPE":
                if value == "dir":
                    if not os.path.isdir(filename):
                        success = 0
                elif value == "file":
                    if not os.path.isfile(filename):
                        success = 0
                elif value == "link":
                    if not os.path.islink(filename):
                        success = 0
            elif case == "PACNEW":
                if not os.path.isfile(f"{filename}.pacnew"):
                    success = 0
            elif case == "PACSAVE":
                if not os.path.isfile(f"{filename}.pacsave"):
                    success = 0
            else:
                tap.diag(f"FILE rule '{case}' not found")
                success = -1
        elif kind == "DIR":
            filename = os.path.join(test.root, key)
            if case == "EXIST":
                if not os.path.isdir(filename):
                    success = 0
            else:
                tap.diag(f"DIR rule '{case}' not found")
                success = -1
        elif kind == "LINK":
            filename = os.path.join(test.root, key)
            if case == "EXIST":
                if not os.path.islink(filename):
                    success = 0
            else:
                tap.diag(f"LINK rule '{case}' not found")
                success = -1
        elif kind == "CACHE":
            cachedir = os.path.join(test.root, util.PM_CACHEDIR)
            if case == "EXISTS":
                pkg = test.findpkg(key, value, allow_local=True)
                if not pkg or not os.path.isfile(
                        os.path.join(cachedir, pkg.filename())):
                    success = 0
        else:
            tap.diag(f"Rule kind '{kind}' not found")
            success = -1

        if self.false and success != -1:
            success = not success
        self.result = success
        return success

# vim: set ts=4 sw=4 et:
