import os
import sys

def pytest_configure(config):
    # Get the directory where this conftest.py file resides
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the package directory
    package_dir = os.path.join(current_dir, 'smahub')

    # Add the package directory to the system path
    sys.path.insert(0, package_dir)
