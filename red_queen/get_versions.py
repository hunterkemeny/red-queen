#!/usr/bin/env python3
"""
Helper script to get available package versions from PyPI.
"""

import sys
import subprocess
import json
from urllib.request import urlopen
from urllib.error import URLError


def get_package_versions(package_name, limit=4):
    """Get available versions for a package from PyPI."""
    try:
        # Try to get versions from PyPI API
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urlopen(url) as response:
            data = json.loads(response.read())
            versions = list(data['releases'].keys())
            
        # Filter out pre-releases and sort by version
        stable_versions = []
        for version in versions:
            if not any(pre in version.lower() for pre in ['rc', 'alpha', 'beta', 'dev']):
                stable_versions.append(version)
        
        # Sort versions (simple string sort, good enough for most cases)
        stable_versions.sort(reverse=True)
        
        return stable_versions[:limit]
        
    except (URLError, json.JSONDecodeError, KeyError):
        # Fallback: try using pip
        try:
            result = subprocess.run(
                ['pip', 'index', 'versions', package_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                versions = []
                for line in lines:
                    if 'Available versions:' in line:
                        version_part = line.split('Available versions:')[1].strip()
                        versions = [v.strip() for v in version_part.split(',')][:limit]
                        break
                return versions
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        # Last resort: return known versions
        fallback_versions = {
            'qiskit': ['1.0', '0.45.0', '0.44.0', '0.43.0'],
            'pytket': ['2.7.0', '2.6.0', '2.5.0', '2.4.1']
        }
        return fallback_versions.get(package_name, [])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 get_versions.py <package_name>")
        sys.exit(1)
        
    package_name = sys.argv[1]
    versions = get_package_versions(package_name)
    
    for version in versions:
        print(version) 