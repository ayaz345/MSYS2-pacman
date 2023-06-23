self.description = "Sync group with ignored packages"

pkg1 = pmpkg("package1")
pkg1.groups = ["grp"]
self.addpkg2db("sync", pkg1)

pkg2 = pmpkg("package2")
pkg2.groups = ["grp"]
self.addpkg2db("sync", pkg2)

pkg3 = pmpkg("package3")
pkg3.groups = ["grp"]
self.addpkg2db("sync", pkg3)

self.option["IgnorePkg"] = ["package1"]
self.args = "--ask=1 -S grp"

self.addrule("PACMAN_RETCODE=0")
self.addrule(f"!PKG_EXIST={pkg1.name}")
self.addrule(f"PKG_EXIST={pkg2.name}")
self.addrule(f"PKG_EXIST={pkg3.name}")
