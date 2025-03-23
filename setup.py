from setuptools import setup, find_packages

setup(
    name="bodytracker_tg_bot",
    version="0.1.0",
    packages=find_packages(),
    long_description=open('README.md').read(),
    install_requires=[
        "python-telegram-bot==20.6",
        "python-dotenv==1.0.1",
    ],
    description="A Telegram bot for tracking body parameters",
    python_requires=">=3.8",
)