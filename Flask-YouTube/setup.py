from setuptools import setup, find_packages

setup(
    name="Flask-YouTube",
    version="0.1",
    license="MIT",
    description="Flask extension to allow easy embedding of YouTube videos",
    author="xxx",
    author_email="xxx@example.com",
    platform="any",
    install_requires=["Flask"],
    packages=find_packages()    # find_packages() 基于一些合理的预设规则，自动找出需要被打包的文件。
)

# 至此，既可以通过下面的命令：
# $ python setup.py build
# $ python setup.py install
# 将代码安装到 Python 目录的 packages 目录下，或者虚拟环境的 packages 目录下。
# 然后再代码中可以通过包名来导入代码：
# from flask_youtube import Youtube