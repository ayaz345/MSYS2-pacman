self.description = "Query info on a package (reverse optdeps)"

pkg = pmpkg("dummy", "1.0-2")
pkg.optdepends = ["dep: for foobar"]
self.addpkg2db("local", pkg)

dep = pmpkg("dep")
self.addpkg2db("local", dep)

self.args = f"-Qi {dep.name}"

self.addrule("PACMAN_RETCODE=0")
self.addrule(f"PACMAN_OUTPUT=^Optional For.*{pkg.name}")
