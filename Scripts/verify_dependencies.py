import importlib
import sys

def verify_dependencies():
    required_packages = [
        ('tensorflow', '2.10.0'),
        ('numpy', '1.21.2'),
        ('pandas', '1.3.3'),
        ('torch', '1.9.0'),
        ('matplotlib', '3.4.3'),
        ('seaborn', '0.11.2')
    ]
    
    print("\n🔍 Verifying Package Installation:")
    all_ok = True
    
    for package, version in required_packages:
        try:
            module = importlib.import_module(package)
            installed_version = module.__version__
            status = '✅' if installed_version == version else '⚠️'
            print(f"{status} {package}: Required={version}, Installed={installed_version}")
            if installed_version != version:
                all_ok = False
        except ImportError:
            print(f"❌ {package}: Not installed")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    success = verify_dependencies()
    if not success:
        print("\n⚠️ Some dependencies have version mismatches or are missing")
        sys.exit(1)
    print("\n✅ All dependencies verified successfully")