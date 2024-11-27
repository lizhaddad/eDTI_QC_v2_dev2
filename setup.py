try:
    from setuptools import setup, find_packages
except (ImportError, ModuleNotFoundError) as e:
    print("Please install setuptools and try again.\npip install setuptools")
    import sys
    sys.exit(1)
else:
    setup(
        name='eDTI_outliers',
        author="Ankush Shetty",
        description="eDTI_outliers is a python-based cli for flagging subjects as outliers depending upond the DTI protocol results.",
        version='0.1.0',
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
        ],
        entry_points={
            'console_scripts': [
                'eDTI_outliers = eDTI_outliers.scripts.cli:main',
                ]
            }
    )