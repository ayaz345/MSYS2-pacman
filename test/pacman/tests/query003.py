self.description = "Query search for a package"

p = pmpkg("foobar")
p.files = ["bin/foobar"]
p.groups = ["group1", "group2"]
self.addpkg2db("local", p)

self.args = f"-Qs {p.name}"

self.addrule("PACMAN_RETCODE=0")
self.addrule(f"PACMAN_OUTPUT=^local/{p.name}")
