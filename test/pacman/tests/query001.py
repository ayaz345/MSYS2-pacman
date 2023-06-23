self.description = "Query a package"

p = pmpkg("foobar")
p.files = ["bin/foobar"]
self.addpkg2db("local", p)

self.args = f"-Q {p.name}"

self.addrule("PACMAN_RETCODE=0")
self.addrule(f"PACMAN_OUTPUT=^{p.name}")
