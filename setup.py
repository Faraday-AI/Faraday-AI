from setuptools import setup, find_packages

setup(
    name="faraday-ai",
    version="1.0.0",
    description="Faraday AI - An AI-powered physical education and learning platform",
    author="Faraday AI Team",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'app': ['*.json', '*.yaml', '*.yml'],
        'app.services.physical_education': ['*.json', '*.yaml', '*.yml'],
    },
    install_requires=[
        # Web Framework
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "gunicorn==21.2.0",
        
        # Database
        "sqlalchemy==2.0.27",
        "alembic==1.13.1",
        "psycopg2-binary==2.9.9",
        
        # Authentication & Security
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.9",
        
        # Data Validation & Settings
        "pydantic==2.6.1",
        "pydantic-settings==2.2.1",
        "python-dotenv==1.0.1",
        
        # Logging & Monitoring
        "loguru==0.7.2",
        "prometheus-client==0.20.0",
        
        # Caching & Queue
        "redis==5.0.1",
        "celery==5.3.6",
        
        # AI & ML
        "tensorflow==2.15.0",
        "torch==2.2.0",
        "scikit-learn==1.4.0",
        "numpy==1.26.4",
        "pandas==2.2.1",
        "opencv-python==4.9.0.80",
        "mediapipe==0.10.9",
        
        # HTTP Client
        "aiohttp==3.9.3",
        "requests==2.31.0",
        
        # Data Visualization
        "plotly==5.18.0",
        "matplotlib==3.8.2",
        "seaborn==0.13.2",
        
        # Utilities
        "networkx==3.2.1",
        "pillow==10.2.0",
        "python-slugify==8.0.4",
    ],
    extras_require={
        'dev': [
            "pytest==8.0.1",
            "pytest-asyncio==0.23.5",
            "pytest-cov==4.1.0",
            "black==24.1.1",
            "flake8==7.0.0",
            "mypy==1.8.0",
            "isort==5.13.2",
        ],
        'docs': [
            "sphinx==7.2.6",
            "sphinx-rtd-theme==2.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
) 