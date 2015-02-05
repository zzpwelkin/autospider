import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "spiderflow",
    version = "0.9",
    author = "zzpwelkin",
    author_email = "zzpwelkin@163.com",
    description = ("Spider flow framework"),
    license = "BSD",
    keywords = "crawler spider framework",
    packages=['spiderflow', 'flowserver'],
    long_description=read('README.md'),
    install_requires =["Flask==0.10.1", # micro web framework
                    "requests", # web client
                    "pymongo", # mongodb python client
                    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Framework",
        "License :: OSI Approved :: BSD License",
    ],
    )