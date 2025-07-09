#!/usr/bin/env python3
"""
Check if the current Python version meets the requirements.
"""
import sys
from packaging import version


def check_python_version():
    """Check if Python version is 3.12 or higher."""
    current_version = version.parse(sys.version)
    required_version = version.parse("3.12")
    
    if current_version < required_version:
        print(f"❌ Python version {current_version} is too old.")
        print(f"   Required: Python 3.12 or higher")
        print(f"   Current:  Python {current_version}")
        sys.exit(1)
    else:
        print(f"✅ Python version {current_version} is compatible.")
        print(f"   Required: Python 3.12 or higher")
        print(f"   Current:  Python {current_version}")


if __name__ == "__main__":
    check_python_version() 