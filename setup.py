from setuptools import setup, find_packages

setup(
    name="faraday-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "sqlalchemy",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.9",
        "pydantic==2.6.1",
        "pydantic-settings==2.2.1",
        "python-dotenv==1.0.1",
        "loguru==0.7.2",
        "redis==5.0.1",
        "tensorflow==2.15.0",
        "torch==2.2.0",
        "scikit-learn==1.4.0",
        "numpy==1.26.4",
        "pandas==2.2.1",
    ],
    python_requires=">=3.8",
) 