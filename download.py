from __future__ import print_function
import os, sys
try:
    from urllib.request import urlopen # Python 3
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import urlopen # Python 2
    from urlparse import urlparse


def get_large_file(url, fname, length=64*1024, retries=3):
    print("Downloading from %s" % url)
    for tnum in range(retries):
        try:
            print("- Try %d for %s: " % (tnum+1, fname), end='')
            req = urlopen(url)
            with open(fname, 'wb') as fp:
                while 1:
                    chunk = req.read(length)
                    if not chunk:
                        break
                    fp.write(chunk)
                    print('.', end='')
                    sys.stdout.flush()
            print(' DONE!')
            return
        except IOError as ierr:
            print("WARNING: failed download of %s cause %s" % (fname, ierr))
    raise RuntimeError("Failed download of %s after %d tries" % (fname, retries))

def list_packages():
    downloadus = set()
    for listfile in os.listdir('.'):
        if not listfile.startswith('elencone-'):
            continue
        with open(listfile) as listf:
            for url in listf.readlines():
                url = url.strip()
                if url.startswith('http'):
                    downloadus.add(url)
    return sorted(downloadus)


if __name__ == "__main__":
    outfolder = sys.argv[1] if len(sys.argv) == 2 else 'tmp' 
    for fileurl in list_packages():
        folder, name = os.path.split(urlparse(fileurl).path)
        archfolder = os.path.join(outfolder, os.path.basename(folder))
        if not os.path.isdir(archfolder):
            os.makedirs(archfolder)
        get_large_file(fileurl, os.path.join(archfolder, name))
    noarch = os.path.join(outfolder, 'noarch')
    if not os.path.isdir(noarch):
        os.makedirs(noarch)
