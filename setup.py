from setuptools import setup


setup(
    name='resumepy',
    version='0.2.0',
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
    python_requires='>=3.5',
    include_package_data=True
)