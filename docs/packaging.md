# Packaging

## Debian package

1. Download & extract the source
2. Open a shell in the source directory
3. Run `cd .. && tar -cJvf youtube-dl-gui_0.4.0.orig.tar.xz youtube-dl-gui && cd youtube-dl-gui && dpkg-buildpackage -rfakeroot`
4. The debian package will be available in the parent directory, install it using `gdebi` or `dpkg -i`
5. You may also run `lintian` on the debian package to check for any bugs or packaging policy related problems.
