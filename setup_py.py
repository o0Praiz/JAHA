#!/usr/bin/env python3
"""
JAH Agency Setup Script
=======================

Installation script for the JAH Agency autonomous AI business management system.

Usage:
    python setup.py install              # Standard installation
    python setup.py develop             # Development installation
    python setup.py sdist               # Create source distribution
    python setup.py bdist_wheel         # Create wheel distribution
    
    pip install -e .                    # Editable development install
    pip install .                       # Standard pip install

Author: JAHA Development Team
Version: 2.0.0
License: MIT
"""

import os
import sys
import re
from pathlib import Path
from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from setuptools.command.develop import develop

# Ensure Python version compatibility
if sys.version_info < (3, 9):
    sys.exit("JAH Agency requires Python 3.9 or higher. Current version: {}".format(sys.version))

# Get the long description from README
def get_long_description():
    """Read the README file for long description"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "JAH Agency - Autonomous AI Business Management System"

# Get version from version file or module
def get_version():
    """Extract version from version file or module"""
    version_file = Path(__file__).parent / "jah_agency" / "_version.py"
    if version_file.exists():
        with open(version_file, 'r') as f:
            version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
            if version_match:
                return version_match.group(1)
    
    # Fallback to main module if version file doesn't exist
    try:
        import jah_agency
        return getattr(jah_agency, '__version__', '2.0.0')
    except ImportError:
        return '2.0.0'

# Read requirements from requirements.txt
def get_requirements():
    """Parse requirements from requirements.txt"""
    requirements_path = Path(__file__).parent / "requirements.txt"
    if not requirements_path.exists():
        return []
    
    requirements = []
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Handle inline comments
                requirement = line.split('#')[0].strip()
                if requirement:
                    requirements.append(requirement)
    
    return requirements

# Get development requirements
def get_dev_requirements():
    """Parse development requirements"""
    dev_requirements_path = Path(__file__).parent / "requirements-dev.txt"
    if not dev_requirements_path.exists():
        # Return common development packages if dev requirements file doesn't exist
        return [
            'pytest>=7.4.3',
            'pytest-asyncio>=0.23.2',
            'pytest-cov>=4.1.0',
            'black>=23.12.0',
            'isort>=5.13.2',
            'flake8>=6.1.0',
            'mypy>=1.8.0',
            'pre-commit>=3.6.0'
        ]
    
    return get_requirements_from_file(dev_requirements_path)

def get_requirements_from_file(filepath):
    """Helper to parse requirements from any file"""
    requirements = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirement = line.split('#')[0].strip()
                    if requirement:
                        requirements.append(requirement)
    except FileNotFoundError:
        pass
    return requirements

# Custom commands for setup
class PostInstallCommand(install):
    """Custom post-installation command"""
    
    def run(self):
        install.run(self)
        self.execute(self._post_install, [], msg="Running post-install tasks...")
    
    def _post_install(self):
        """Tasks to run after installation"""
        print("\n🎉 JAH Agency installation completed!")
        print("=" * 50)
        
        # Create necessary directories
        directories = [
            'logs',
            'config',
            'data',
            'backups',
            'temp'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        
        # Copy example configuration if it doesn't exist
        config_example = Path("config") / "config.example.yaml"
        config_main = Path("config") / "config.yaml"
        
        if config_example.exists() and not config_main.exists():
            import shutil
            shutil.copy2(config_example, config_main)
            print(f"✅ Created configuration file: {config_main}")
        
        print("\n📋 Next Steps:")
        print("1. Copy and customize config/config.yaml")
        print("2. Set up your environment variables")
        print("3. Initialize the database: python -m jah_agency.scripts.init_db")
        print("4. Start the system: python main.py")
        print("\n📖 Documentation: https://github.com/o0Praiz/JAHA")


class PostDevelopCommand(develop):
    """Custom post-development installation command"""
    
    def run(self):
        develop.run(self)
        self.execute(self._post_develop, [], msg="Setting up development environment...")
    
    def _post_develop(self):
        """Tasks to run after development installation"""
        print("\n🔧 Development environment setup completed!")
        print("=" * 50)
        
        # Install pre-commit hooks
        try:
            import subprocess
            result = subprocess.run(['pre-commit', 'install'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Pre-commit hooks installed")
            else:
                print("⚠️  Pre-commit hooks installation failed")
        except FileNotFoundError:
            print("⚠️  Pre-commit not found, skipping hooks installation")
        
        print("\n🛠️  Development tools available:")
        print("- pytest: Run tests")
        print("- black: Code formatting")
        print("- isort: Import sorting")
        print("- flake8: Code linting")
        print("- mypy: Type checking")


class CleanCommand(Command):
    """Custom clean command to remove build artifacts"""
    
    description = 'Clean build artifacts'
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Remove build artifacts"""
        import shutil
        
        artifacts = [
            'build',
            'dist',
            '*.egg-info',
            '__pycache__',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.mypy_cache',
            '.tox'
        ]
        
        for pattern in artifacts:
            for path in Path('.').glob(f'**/{pattern}'):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"🗑️  Removed directory: {path}")
                    else:
                        path.unlink()
                        print(f"🗑️  Removed file: {path}")


class TestCommand(Command):
    """Custom test command"""
    
    description = 'Run the test suite'
    user_options = [
        ('coverage', 'c', 'Run with coverage report'),
        ('verbose', 'v', 'Verbose output'),
        ('parallel', 'p', 'Run tests in parallel'),
    ]
    
    def initialize_options(self):
        self.coverage = False
        self.verbose = False
        self.parallel = False
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Run tests using pytest"""
        import subprocess
        
        cmd = ['python', '-m', 'pytest']
        
        if self.verbose:
            cmd.append('-v')
        
        if self.coverage:
            cmd.extend(['--cov=jah_agency', '--cov-report=html', '--cov-report=term'])
        
        if self.parallel:
            cmd.extend(['-n', 'auto'])
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        sys.exit(result.returncode)


# Package configuration
setup(
    # Basic package information
    name="jah-agency",
    version=get_version(),
    author="JAHA Development Team",
    author_email="dev@jahagency.com",
    description="Autonomous AI Business Management System",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/o0Praiz/JAHA",
    
    # Package discovery
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    package_data={
        'jah_agency': [
            'templates/*.html',
            'templates/*.txt',
            'static/*',
            'config/*.yaml',
            'config/*.json',
            'schemas/*.json',
            'migrations/*.sql'
        ]
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=get_requirements(),
    extras_require={
        'dev': get_dev_requirements(),
        'test': [
            'pytest>=7.4.3',
            'pytest-asyncio>=0.23.2',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.12.0',
            'factory-boy>=3.3.0'
        ],
        'docs': [
            'sphinx>=7.2.6',
            'sphinx-rtd-theme>=2.0.0',
            'mkdocs>=1.5.3',
            'mkdocs-material>=9.5.3'
        ],
        'monitoring': [
            'prometheus-client>=0.19.0',
            'opentelemetry-api>=1.22.0',
            'opentelemetry-sdk>=1.22.0',
            'sentry-sdk[fastapi]>=1.39.2'
        ],
        'ml': [
            'tensorflow>=2.15.0',
            'torch>=2.1.2',
            'scikit-learn>=1.3.2',
            'xgboost>=2.0.2'
        ],
        'blockchain': [
            'web3>=6.15.1',
            'eth-account>=0.10.0'
        ],
        'full': [
            # Include all extras
            'pytest>=7.4.3', 'pytest-asyncio>=0.23.2', 'pytest-cov>=4.1.0',
            'sphinx>=7.2.6', 'sphinx-rtd-theme>=2.0.0',
            'prometheus-client>=0.19.0', 'sentry-sdk[fastapi]>=1.39.2',
            'tensorflow>=2.15.0', 'torch>=2.1.2', 'scikit-learn>=1.3.2',
            'web3>=6.15.1'
        ]
    },
    
    # Python version requirement
    python_requires=">=3.9",
    
    # Console scripts / entry points
    entry_points={
        'console_scripts': [
            'jah-agency=jah_agency.cli:main',
            'jah-agent=jah_agency.main:main',
            'jah-setup=jah_agency.scripts.setup:main',
            'jah-migrate=jah_agency.scripts.migrate:main',
            'jah-backup=jah_agency.scripts.backup:main',
        ],
    },
    
    # Classification metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
        "Natural Language :: English",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "ai", "artificial-intelligence", "autonomous", "business", "automation",
        "agent", "multi-agent", "revenue-generation", "financial", "freelancing",
        "task-management", "workflow", "machine-learning", "nlp"
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/o0Praiz/JAHA/issues",
        "Source": "https://github.com/o0Praiz/JAHA",
        "Documentation": "https://github.com/o0Praiz/JAHA/docs",
        "Changelog": "https://github.com/o0Praiz/JAHA/blob/main/CHANGELOG.md",
        "Funding": "https://github.com/sponsors/o0Praiz",
    },
    
    # Custom commands
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
        'clean': CleanCommand,
        'test': TestCommand,
    },
    
    # Zip safety
    zip_safe=False,
    
    # License
    license="MIT",
    
    # Platforms
    platforms=["any"],
)