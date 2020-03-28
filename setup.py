from setuptools import setup, find_packages


setup(
    name='resumepy',
    version=0.1,
    package_dir={'': 'src'},
    packages=['resumepy'],
    entry_points={
        'console_scripts': [
            'resumepy = resumepy.cli:cli'
        ]
    },
    install_requires=[
        'click>=7.1.1',
        'pyyaml>=5.3.1',
        'pdfkit>=0.6.1',
        'jinja2>=2.11.1'
    ],
    include_package_data=True,
    python_requires='>=3.5'
)