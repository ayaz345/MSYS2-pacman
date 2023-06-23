self.description = "Install a package (wrong architecture, auto)"

import os
machine = os.uname()[4]

p = pmpkg("dummy")
p.files = ["bin/dummy",
           "usr/man/man1/dummy.1"]
p.arch = f'{machine}wrong'
self.addpkg(p)

self.option["Architecture"] = ['auto']

self.args = f"-U {p.filename()}"

self.addrule("PACMAN_RETCODE=1")
self.addrule("!PKG_EXIST=dummy")
for f in p.files:
	self.addrule(f"!FILE_EXIST={f}")
