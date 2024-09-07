from setuptools import find_packages, setup

__version__ = "" 
exec(open("version.py").read())
setup(
    name="actual-pluggy-py",
    version=__version__,
    packages=find_packages(),
    description="Brazilian Bank Sync for Actual with Pluggy using Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Thiago Campanate",
    author_email="tcampanate@gmail.com",
    url="https://github.com/tcpr1/actualpluggy",
    zip_safe=False,
    project_urls={
        "Issues": "https://github.com/tcpr1/actualpluggy/issues",
    },
    install_requires=["actualpy", "python-dateutil", "requests"],
)