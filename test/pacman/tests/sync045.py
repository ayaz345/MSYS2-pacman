self.description = "Install a sync package conflicting with two local ones (-dd)"

sp = pmpkg("pkg1")
sp.conflicts = ["pkg2", "pkg3"]
self.addpkg2db("sync", sp);

lp1 = pmpkg("pkg2")
self.addpkg2db("local", lp1);

lp2 = pmpkg("pkg3")
self.addpkg2db("local", lp2);

self.args = f"-Sdd {sp.name} --ask=4"

self.addrule("PACMAN_RETCODE=0")
self.addrule("PKG_EXIST=pkg1")
self.addrule("!PKG_EXIST=pkg2")
self.addrule("!PKG_EXIST=pkg3")
