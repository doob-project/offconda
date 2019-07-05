from __future__ import print_function
import os, sys, time, re, json
from tempfile import mkdtemp
from packaging import version
try:
    from urllib.request import urlopen  # Python 3
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import urlopen  # Python 2
    from urlparse import urlparse
import ssl

MAINCONDAREPO = "https://repo.anaconda.com/pkgs/main"

def splitcondaname(cname):
    xx = cname.split('-')
    variant = xx.pop().split('.')[0]
    ver = xx.pop()
    base = '-'.join(xx)
    return base, version.parse(ver), variant


def find_all_packages(platform):
    cname = '{}-cache.json'.format(platform)
    if os.path.isfile(cname):
        with open(cname) as cf:
            return json.load(cf)
    descurl = "https://repo.anaconda.com/pkgs/main/{}/".format(platform)
    req = urlopen(descurl)
    body = req.read()
    req.close()
    findpack = re.compile('\s+<td><a href="(.*?\.tar\.bz2)"')
    allpacks = set()
    for row in body.splitlines():
        found = findpack.match(row)
        if not found:
            continue
        pname = found.group(1)
        if pname.startswith("_"):
            continue
        allpacks.add(found.group(1))
    allpacks = sorted(allpacks)
    with open(cname, "wt") as cf:
        json.dump(allpacks, cf, indent=2)
    return sorted(allpacks)


def get_large_file(url, fname, length=64*1024, retries=5, overwrite=False):
    print("Downloading %s -> %s" % (url, fname))
    ssl._https_verify_certificates(True)
    for tnum in range(retries):
        try:
            print("- Try %d: " % (tnum+1), end='')
            req = urlopen(url)
            size = long(req.headers['content-length'])
            if not overwrite and os.path.exists(fname) and os.stat(fname).st_size == size:
                print("Skipping becuase existing with size {} B".format(size))
                return
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
            time.sleep(tnum+1)
            if tnum > 1:
                print("WARNING: Disabling SSL certificates verification")
                ssl._https_verify_certificates(False)
    raise RuntimeError("Failed download of %s after %d tries" % (fname, retries))


def list_packages(elencone='', where=".", allvariants=False, acceptallorigins=False):
    allv = dict()
    if allvariants:
        for k in ('linux-64', 'win-64', 'noarch'):
            allv[k] = find_all_packages(k)
    downloadus = set()
    for listfile in os.listdir(where):
        if elencone and listfile == elencone or not elencone and listfile.startswith('elencone-'):
            with open(os.path.join(where, listfile)) as listf:
                urls = listf.readlines()
                while urls:
                    url = urls.pop().strip()
                    if url in downloadus or not url.startswith('http'):
                        continue
                    downloadus.add(url)
                    if allvariants and (url.startswith(MAINCONDAREPO) or acceptallorigins):
                        pp = url.split('/')
                        pname = pp.pop()
                        arch = pp.pop()
                        archvar = allv[arch]
                        assert acceptallorigins or pname in archvar
                        base, ver = splitcondaname(pname)[0:2]
                        for candidate in archvar:
                            if candidate == pname:
                                continue
                            bc, bver = splitcondaname(candidate)[0:2]
                            if bc != base or ver.base_version != bver.base_version:
                                continue
                            dwnurl = '/'.join([MAINCONDAREPO, arch, candidate])
                            downloadus.add(dwnurl)
                            print("Found variant of {}: {} -- {}".format(pname, candidate, dwnurl))
    return sorted(downloadus)


def main(outfolder='', elencone='', where='.', overwrite=False, allvariants=False, acceptallorigins=False):
    if not outfolder:
        outfolder = mkdtemp(prefix="offconda-")
    for fileurl in list_packages(elencone, where, allvariants, acceptallorigins):
        folder, name = os.path.split(urlparse(fileurl).path)
        archfolder = os.path.join(outfolder, os.path.basename(folder))
        if not os.path.isdir(archfolder):
            os.makedirs(archfolder)
        get_large_file(fileurl, os.path.join(archfolder, name), overwrite=overwrite)
    noarch = os.path.join(outfolder, 'noarch')
    if not os.path.isdir(noarch):
        os.makedirs(noarch)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Conda Packages download")
    parser.add_argument('-o', '--outfolder', default="", help='Output folder')
    parser.add_argument('-e', '--ename', default="", help='File name of the packages list')
    parser.add_argument('-w', '--workfolder', default=".", help='Working folder containing the lists')
    parser.add_argument('-a', '--allvariants', action='store_true', help="Search for all packages variants")
    parser.add_argument('-x', '--crossorigins', action='store_true', help="Search variants accross origins")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite existings files")
    args = parser.parse_args()
    main(args.outfolder, args.ename, args.workfolder, args.overwrite, args.allvariants, args.crossorigins)
