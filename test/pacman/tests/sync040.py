self.description = "Install two targets from a sync db with a conflict"

sp1 = pmpkg("pkg1")
sp1.conflicts = ["pkg2"]

sp2 = pmpkg("pkg2")

for p in sp1, sp2:
	self.addpkg2db("sync", p);

self.args = f'-S {" ".join([p.name for p in (sp1, sp2)])}'

self.addrule("PACMAN_RETCODE=1")
for p in sp1, sp2:
	self.addrule(f"!PKG_EXIST={p.name}")
