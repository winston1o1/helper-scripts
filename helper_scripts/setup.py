from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text()

setup(
    name = 'helper_scripts',
    packages = ['database_handler','send_mail','google_drive'],
    version='0.4.0',
    author='Samuel Kizza & Winston Ssentongo',
    author_email= 'winstondavid96@gmail.com',
    maintainer='Winston David Ssentongo',
    maintainer_email='winstondavid96@gmail.com',
    description='Database Helper Package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/winston1o1/helper-scripts',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
    "psycopg2",
    "google-api-python-client"
    ]
)