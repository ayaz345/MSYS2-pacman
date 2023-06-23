self.description = "Quick check for using XferCommand"

# this setting forces us to download packages
self.cachepkgs = False
#wget doesn't support file:// urls.  curl does
self.option['XferCommand'] = ['/usr/bin/curl %u > %o']

numpkgs = 10
pkgnames = []
for i in range(numpkgs):
    name = f"pkg_{i}"
    pkgnames.append(name)
    p = pmpkg(name)
    p.files = [f"usr/bin/foo-{i}"]
    self.addpkg2db("sync", p)

self.args = f"-S {' '.join(pkgnames)}"

for name in pkgnames:
    self.addrule(f"PKG_EXIST={name}")
