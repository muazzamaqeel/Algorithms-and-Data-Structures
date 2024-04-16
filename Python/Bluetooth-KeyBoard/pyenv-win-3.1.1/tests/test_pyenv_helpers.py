import os
import shutil
import subprocess
from contextlib import contextmanager
from packaging import version
from pathlib import Path


@contextmanager
def working_directory(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def python_exes(suffixes=None):
    if suffixes is None:
        suffixes = [""]
    else:
        suffixes.append("")
    for suffix in suffixes:
        yield f'python{suffix}.exe'
        yield f'pythonw{suffix}.exe'


def script_exes(ver):
    for suffix in ['', f'{ver.major}', f'{ver.major}.{ver.minor}']:
        yield f'pip{suffix}.exe'
    for suffix in ['', f'-{ver.major}.{ver.minor}']:
        yield f'easy_install{suffix}.exe'


def touch(exe):
    with open(exe, 'a'):
        os.utime(exe, None)


def pyenv_setup(settings):
    pyenv_path, local_path, versions, global_ver, local_ver = \
        settings['pyenv_path'], \
        settings['local_path'], \
        settings.get('versions', None), \
        settings.get("global_ver", None), \
        settings.get('local_ver', None)
    if versions is None:
        versions = []
    if isinstance(global_ver, list):
        global_ver = '\n'.join(global_ver)
    if isinstance(local_ver, list):
        local_ver = '\n'.join(local_ver)
    src_path = Path(__file__).resolve().parents[1].joinpath('pyenv-win')
    dirs = [r'bin', r'libexec\libs', r'shims', r'versions']
    for d in dirs:
        os.makedirs(Path(pyenv_path, d))
    _, _, libexec_files = next(os.walk(src_path.joinpath('libexec')))
    for f in libexec_files:
        shutil.copy(Path(src_path, 'libexec', f), Path(pyenv_path, 'libexec', f))
    files = [r'.versions_cache.xml',
             r'..\.version',
             r'bin\pyenv.bat',
             r'bin\pyenv.ps1',
             r'libexec\pyenv-shell.bat',
             r'libexec\libs\pyenv-install-lib.vbs',
             r'libexec\libs\pyenv-lib.vbs']
    for f in files:
        shutil.copy(src_path.joinpath(f), Path(pyenv_path, f))
    versions_dir = Path(pyenv_path, r'versions')

    def create_pythons(path):
        os.mkdir(path)
        for exe in python_exes([f'{ver.major}', f'{ver.major}{ver.minor}', f'{ver.major}.{ver.minor}']):
            touch(path.joinpath(exe))
        with open(path.joinpath('version.bat'), "w") as batch:
            print(f"@echo {ver.major}.{ver.minor}.{ver.micro}", file=batch)
        return path

    def create_scripts(path):
        os.mkdir(path)
        for exe in script_exes(ver):
            touch(path.joinpath(exe))
        with open(path.joinpath('hello.bat'), "w") as batch:
            print("@echo Hello world!", file=batch)
        with open(path.joinpath('version.bat'), "w") as batch:
            print(f"@echo {ver.major}.{ver.minor}.{ver.micro}", file=batch)

    for v in versions:
        ver = version.parse(v.version)
        version_path = create_pythons(versions_dir.joinpath(v))
        create_scripts(version_path.joinpath('Scripts'))
    if global_ver is not None:
        with open(Path(pyenv_path, "version"), "w") as f:
            print(global_ver, file=f)
    if local_ver is not None:
        with open(Path(local_path, ".python-version"), "w") as f:
            print(local_ver, file=f)


def not_installed_output(ver):
    return (f"pyenv specific python requisite didn't meet. "
            f"Project is using different version of python.\r\n"
            f"Install python '{ver}' by typing: 'pyenv install {ver}'")


def global_python_versions(path):
    with open(Path(path, 'version'), mode='r') as f:
        return f.read().strip()


def local_python_versions(path):
    with open(Path(path, '.python-version'), mode='r') as f:
        return f.read().strip()


def do_run(*args, env={}):
    args = list(args)
    result = subprocess.run(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stderr = str(result.stderr, "utf-8").strip()
    # \x0c: generated by cls in cmd AutoRun
    stdout = str(result.stdout, "utf-8").rpartition('\x0c')[2].strip("\r\n")
    return stdout, stderr


class Arch(str):
    version = None

    def __new__(cls, content):
        self = super().__new__(cls, content)
        self.version = content
        return self


class Native(Arch):
    def __new__(cls, content):
        ver = content
        if os.environ['PYENV_FORCE_ARCH'] == 'X86':
            content = content + '-win32'
        self = super().__new__(cls, content)
        self.version = ver
        return self


class X86(Arch):
    def __new__(cls, content):
        ver = content
        content = content + '-win32'
        self = super().__new__(cls, content)
        self.version = ver
        return self


class Amd64(Arch):
    def __new__(cls, content):
        ver = content
        content = content + '-amd64'
        self = super().__new__(cls, content)
        self.version = ver
        return self
