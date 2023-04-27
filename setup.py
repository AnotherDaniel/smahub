from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smahub",
    version="0.5.0",
    author="Daniel Krippner",
    author_email="dk.mailbox@gmx.net",
    description="Little daemon that runs plugins for collecting data from SMA PV products, and publishes to eg MQTT via other plugins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AnotherDaniel/smahub",
    packages=find_packages(where="smahub"),
    package_dir={"": "smahub", "utils": "smahub/utils"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License 2.0 (Apache-2.0)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        'requests',
        'paho-mqtt'
    ],
    extras_require={
        # List any optional or extra dependencies here
    },
)