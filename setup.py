from setuptools import setup

setup(
    name="bodytracker_tg_bot",
    version="0.1.0",
    py_modules=["BodyTracker_tg-bot"],  # Указываем основной файл
    long_description=open('README.md', encoding='utf-8').read(),
    install_requires=[
        "python-telegram-bot==20.6",
        "python-dotenv==1.0.1",
    ],
    description="A Telegram bot for tracking body parameters",
    python_requires=">=3.8",
)