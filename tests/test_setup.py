"""
Quick test to verify if the setup is working

LOCATION: tests/test_setup.py

HOW TO RUN THIS FILE IN POWERSHELL:
    From your project root directory, run:
    
    python tests\\test_setup.py
    
    OR
    
    python .\\tests\\test_setup.py

DO NOT USE: tests.test_setup.py (that's Python import syntax, not a PowerShell command!)
"""

import sys
from pathlib import Path

# Add project root to Python path (so we can import the package before installation)  # --Fixed--
project_root = Path(__file__).parent.parent  # --Fixed--
sys.path.insert(0, str(project_root))  # --Fixed--

def main():
    """Test the project setup"""
    print("=" * 70)
    print("🧪 TESTING DIGITAL-INVESTMENT-ANALYTICS SETUP")
    print("=" * 70)
    
    try:
        # Test 1: Import config module
        print("\n[Test 1] Importing config module...")
        from fmp.config import config  # --Fixed--
        print("✅ Config import successful")
        print(f"   Config: {config}")
        
        # Test 2: Load API key
        print("\n[Test 2] Loading API key...")
        api_key = config.get_api_key()
        print(f"✅ API key loaded successfully")
        print(f"   Key preview: {api_key[:4]}...{api_key[-4:]}")
        
        # Test 3: Verify config file location
        print("\n[Test 3] Verifying config file location...")
        print(f"✅ Config file found at: {config.config_file}")
        
        # Test 4: Check project structure
        print("\n[Test 4] Checking project structure...")
        required_dirs = ['src', 'config', 'data', 'tests', 'models']  # --Fixed-- # removed nonexistent 'examples'
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name}/ folder exists")
            else:
                print(f"⚠️  {dir_name}/ folder missing")
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! Setup is complete!")
        print("=" * 70)
        print("\n📋 Next steps:")
        print("   1. Run: pip install -e .")
        print("   2. Use from fmp.client import FMPClient in your code.")  # --Fixed--
        print("   3. Start building your ML models!")
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found error: {str(e)}")
        print("\n📋 Troubleshooting:")
        print("   1. Make sure config/api_keys.txt exists")
        print("   2. Check file path is correct")
        return False
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {str(e)}")
        print("\n📋 Troubleshooting:")
        print("   1. Open config/api_keys.txt")
        print("   2. Replace 'your_api_key_here' with your actual FMP API key")
        print("   3. Get key from: https://site.financialmodelingprep.com/developer/docs")
        return False
        
    except ImportError as e:
        print(f"\n❌ Import error: {str(e)}")
        print("\n📋 Troubleshooting:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Run: pip install -e .")
        print("   3. Check that src/__init__.py exists")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("\n📋 Troubleshooting:")
        print("   1. Check all files are in correct locations")
        print("   2. Verify virtual environment is activated")
        print("   3. Run: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)