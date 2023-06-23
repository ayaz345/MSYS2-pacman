self.description = "Query info on a package (optdep install status [uninstalled])"

optstr = "dep: for foobar"

pkg = pmpkg("dummy", "1.0-2")
pkg.optdepends = [optstr]
self.addpkg2db("local", pkg)

self.args = f"-Qi {pkg.name}"

self.addrule("PACMAN_RETCODE=0")
self.addrule(f"PACMAN_OUTPUT=^Optional Deps.*{optstr}$")
