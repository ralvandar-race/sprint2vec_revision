import sys
import pkg_resources
import importlib

def verify_packages():
    """Verify installed package versions"""
    with open('requirements.txt') as f:
        requirements = [
            line.strip().split('==')[0] 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]
    
    print("\n📦 Package Version Check:")
    all_ok = True
    
    for package in requirements:
        try:
            if package.endswith('+cpu'):
                package = package.split('+')[0]
            module = importlib.import_module(package)
            version = pkg_resources.get_distribution(package).version
            print(f"✅ {package}: {version}")
        except (ImportError, pkg_resources.DistributionNotFound):
            print(f"❌ {package}: Not found")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    if verify_packages():
        print("\n✅ All packages installed successfully")
        sys.exit(0)
    else:
        print("\n❌ Some packages are missing")
        sys.exit(1)