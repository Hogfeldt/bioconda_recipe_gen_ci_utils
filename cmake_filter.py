import urllib.request
import os
import tempfile
import tarfile
import zipfile
import sys

from packagedb import PackageDBResource
from utils import get_brg_ci_homedir_path

CI_HOMEDIR = get_brg_ci_homedir_path()
PACKAGE_CHANGED_DB_PATH = CI_HOMEDIR + "/packages_changed.yaml"
PACKAGES_FILTERED_ON_CMAKE = CI_HOMEDIR + "/cmake_packages.yaml"

BUILD_FILES = ['cmakelists.txt', 'setup.py']

def download_and_unpack_source(src, dir_path):
    """ Download a source file and unpack it """
    try:
        # .tar
        if src.lower().endswith(".tar"):
            urllib.request.urlretrieve(src, "%s/source.tar" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tar" % dir_path) as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .tar.gz
        if src.lower().endswith(".tar.gz"):
            urllib.request.urlretrieve(src, "%s/source.tar.gz" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tar.gz" % dir_path, "r:gz") as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .tar.bz2
        elif src.lower().endswith(".tar.bz2"):
            urllib.request.urlretrieve(src, "%s/source.tar.bz2" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tar.bz2" % dir_path, "r:bz2") as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .tgz
        elif src.lower().endswith(".tgz"):
            urllib.request.urlretrieve(src, "%s/source.tgz" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tgz" % dir_path, "r:gz") as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .zip
        elif src.lower().endswith(".zip"):
            urllib.request.urlretrieve(src, "%s/source.zip" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with zipfile.ZipFile("%s/source.zip" % dir_path, "r") as zip_ref:
                zip_ref.extractall("%s/source" % dir_path)
        else:
            print("Unknown fileformat! Cannot unpack %s" % src)
    except urllib.error.HTTPError as e:
        print('HTTP error code: ', e.code)
        print(src)
    except urllib.error.URLError as e:
        print('URL error Reason: ', e.reason)
        print(src)
    except tarfile.ReadError:
        print('Tarfile ReadError')
        print(src)
    except:
        print("Unexpected error:", sys.exc_info()[0])

def find_build_files(path):
    files_of_interest = []
    for root, dirs, files in os.walk(path):
        for f in files:
            f.lower()
        for f in files:
            if f in BUILD_FILES:
                files_of_interest.extend(os.path.join(root,f))
    return files_of_interest
    

def filter_out_packages_without_cmakelist():
    """ From a list of (Name, Source_urls), download and unpack source, then
        check if root of file tree contains a CMakeList.txt.
        Return list of tupple (Name, Source_urls).
        """
    packages_to_filter = dict()
    filtere_packages = dict()
    with PackageDBResource(PACKAGE_CHANGED_DB_PATH) as packageDB:
        packages_to_filter = packageDB.get_new_packages()
        if packages_to_filter is None:
            return
    print(packages_to_filter)
    for name, source in packages_to_filter.items():
        with tempfile.TemporaryDirectory() as tmpdir:
            download_and_unpack_source(source, tmpdir)
            files_of_interest = find_build_files(os.path.join(tmpdir, 'source'))
            for file in files_of_interest:
                if 'cmakelists.txt' in file:
                    filtere_packages.update({name : source})
                    print('Added package: ' +name+ " "+source)
    with PackageDBResource(PACKAGES_FILTERED_ON_CMAKE) as packageDB:
        packageDB.add_new_packages(filtere_packages)
    print(filtere_packages)


if __name__ == '__main__':
    filter_out_packages_without_cmakelist()
