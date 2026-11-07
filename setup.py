from setuptools import setup

setup(
    name="mixed_in_key_automator",
    version="2.0.0",
    description="Windows automator and database tools for Mixed In Key 11",
    author="Blake Vandercar",
    author_email="TODO",
    packages=["mik_automator"],
    package_dir={"mik_automator": "src"},
    python_requires=">=3.10",
    install_requires=["pywinauto>=0.6.9", "pywin32", "comtypes"],
)
