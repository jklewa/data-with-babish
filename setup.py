import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "beautifulsoup4",
    "click",
    "flask",
    "flask-migrate",
    "flask-sqlalchemy",
    "furl",
    "html5lib",
    "measurement",
    "psycopg2-binary",
    "pyfunctional",
    "requests",
]

setuptools.setup(
    name="babish-db",
    version="0.0.1",
    license='GPLv3+',
    author="jklewa",
    author_email="jklewa@gmail.com",
    description="Data with Babish DB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jklewa/data-with-babish",
    scripts=[
        "ibdb/bin/ibdb",
    ],
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
