### to build the application as package so it can be used easily for deployment etc
from typing import List
from setuptools import setup, find_packages
def get_requirements(file_path:str)->List[str]:
    '''
    this function will return list of requirements
    '''
    requirements = []
    try:
        with open(file_path, encoding="utf-8") as file_obj:
            requirements = file_obj.readlines()
            requirements = [req.replace("\n","") for req in requirements]

            if "-e ." in requirements:
                requirements.remove("-e .")
    except FileNotFoundError:
        requirements = []

    return requirements

setup(
    name="Web Scraping Project",
    version="0.1",
    author="Umar",
    author_email="muhammadumar19987@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)