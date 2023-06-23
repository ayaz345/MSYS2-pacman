self.description = "-Su foo"

sp1 = pmpkg("pkg1", "1.0-2")
sp1.depends = ["pkg2"]

sp2 = pmpkg("pkg2")
sp2.depends = ["pkg3"]

sp3 = pmpkg("pkg3")

sp4 = pmpkg("pkg4")

for p in sp1, sp2, sp3, sp4:
	self.addpkg2db("sync", p)

lp1 = pmpkg("pkg1")
self.addpkg2db("local", lp1)

self.args = f"-Su {sp4.name}"

self.addrule("PACMAN_RETCODE=0")
self.addrule("PKG_VERSION=pkg1|1.0-2")
for p in sp2, sp3:
	self.addrule(f"PKG_REASON={p.name}|1")
self.addrule(f"PKG_REASON={sp4.name}|0")
