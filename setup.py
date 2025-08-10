from setuptools import setup, find_packages

setup(
    name="carqrsticker",
    version="0.1",
    packages=find_packages(),
    package_data={
        "src": ["assets/*", "static/*"],
    },
    include_package_data=True,
    install_requires=[
        "qrcode",
        "Pillow",
        "fpdf2",
        "pytest",
        "pytest-cov",
    ],
    entry_points={
        "console_scripts": [
            "carqrsticker=src.main:main",
        ],
    },
)
