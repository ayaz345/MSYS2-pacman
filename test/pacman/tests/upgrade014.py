self.description = "Install two packages with a conflicting file (--force)"

p1 = pmpkg("dummy")
p1.files = ["bin/dummy",
            "usr/man/man1/dummy.1",
            "usr/common"]

p2 = pmpkg("foobar")
p2.files = ["bin/foobar",
            "usr/man/man1/foobar.1",
            "usr/common"]

for p in p1, p2:
	self.addpkg(p)

self.args = f'-U --force {" ".join([p.filename() for p in (p1, p2)])}'

self.addrule("PACMAN_RETCODE=0")
for p in p1, p2:
	self.addrule(f"PKG_EXIST={p.name}")
	self.addrule(f"PKG_FILES={p.name}|usr/common")
	for f in p.files:
		self.addrule(f"FILE_EXIST={f}")
