self.description = "Get URL on package from a sync db"

sp = pmpkg("dummy")
sp.files = ["bin/dummy",
            "usr/man/man1/dummy.1"]
self.addpkg2db("sync", sp)

self.args = f"-Sp {sp.name}"

self.addrule("PACMAN_RETCODE=0")
self.addrule(f"PACMAN_OUTPUT={sp.name}")
self.addrule("PACMAN_OUTPUT=file://")
