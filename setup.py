from setuptools import setup, find_packages

setup(
    name="jobqueue_server",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["flask", "pandas"],
    entry_points={
        'console_scripts': [
        'jq-server=jobqueue_server.__main__:run',
        'jq-gui = jobqueue_server.gui:run_gui'
        ]
    },
)
