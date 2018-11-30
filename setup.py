import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command


NAME = 'lium_diarization_editor'
DESCRIPTION = 'Editor/viewer for LIUM diarizations.'
URL = 'https://github.com/maxhollmann/lium-diarization-editor'
EMAIL = 'maxhollmann@gmail.com'
AUTHOR = 'Max Hollmann'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.1'

REQUIRED = [
    'python-mpv',
    'matplotlib',
    'click',
    'pandas',
]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires=REQUIRES_PYTHON,
    packages=['lium_diarization_editor'],
    license='MIT',
    entry_points={
        'console_scripts': ['lium-dia-edit=lium_diarization_editor.cli:main'],
    },
    install_requires=REQUIRED,
    cmdclass={
        'upload': UploadCommand,
    },
)
