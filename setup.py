import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_requirements = {
    "dev": ["wheel", "black"],
}

setuptools.setup(
    name="perftester",
    version="0.7.0",
    author="Nyggus",
    author_email="nyggus@gmail.com",
    description="Lightweight performance testing in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nyggus/perftester",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["easycheck", "rounder", "memory_profiler", "pympler"],
    python_requires=">=3.8",
    extras_require=extras_requirements,
    entry_points={
        "console_scripts": ["perftester = perftester.__main__:main"]
    },
)
