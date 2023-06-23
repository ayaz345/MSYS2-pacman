self.description = "Install a package with multiple missing dependencies"

p = pmpkg("dummy")
p.files = ["bin/dummy",
           "usr/man/man1/dummy.1"]
p.depends = ["dep1", "dep2", "dep3"]
self.addpkg(p)

p2 = pmpkg("dep2")
self.addpkg(p2)

self.args = f"-U {p.filename()} {p2.filename()}"

self.addrule("PACMAN_RETCODE=1")
self.addrule("!PKG_EXIST=dummy")
for f in p.files:
	self.addrule(f"!FILE_EXIST={f}")
