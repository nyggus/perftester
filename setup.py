import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_requirements = {
    "dev": ["wheel==0.37.1", "black"],
}

setuptools.setup(
    name="perftest",
    version="0.2.1",
    author="Nyggus",
    author_email="nyggus@gmail.com",
    description="Lightweight performance testing in Python",
    long_description=long_description,
    long_description_content_type="text/x-md",
    url="https://github.com/nyggus/perftest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["easycheck", "rounder", "memory_profiler==0.60.0"],
    python_requires=">=3.6",
    extras_require=extras_requirements,
    entry_points={"console_scripts": ["perftest = perftest.__main__:main"]},
)
