import setuptools

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='serial-visualisation',
    version='1.0.5',
    author='ES-Alexander',
    author_email='sandman.esalexander@gmail.com',
    description='A package for visualisation of serial data in a grid.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ES-Alexander/serial-visualisation',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'opencv-python',
        'pyserial',
    ],
)
