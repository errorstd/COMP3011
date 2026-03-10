"""
Master Test Runner
Executes all test suites and generates summary report
"""

import sys
import subprocess
from datetime import datetime


def run_test_file(test_file):
    """Run a single test file and return results"""
    print(f"\n{'='*70}")
    print(f"🧪 Running: {test_file}")
    print('='*70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            return True, f"✅ {test_file} - PASSED"
        else:
            return False, f"❌ {test_file} - FAILED"
            
    except Exception as e:
        return False, f"❌ {test_file} - ERROR: {str(e)}"


def main():
    """Run all tests and generate report"""
    
    print("\n" + "="*70)
    print("🚀 STOCK VALUATION & RISK ANALYTICS API - TEST SUITE")
    print("="*70)
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    test_files = [
        "tests/test_db_connection.py",
        "tests/test_analytics.py",
        "tests/test_api.py"
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_file in test_files:
        success, message = run_test_file(test_file)
        results.append(message)
        
        if success:
            passed += 1
        else:
            failed += 1
    
    # Generate summary report
    print("\n" + "="*70)
    print("📊 TEST SUMMARY REPORT")
    print("="*70)
    
    for result in results:
        print(result)
    
    print("\n" + "="*70)
    print(f"Total Tests: {len(test_files)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_files)*100):.1f}%")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! API is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {failed} test suite(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
