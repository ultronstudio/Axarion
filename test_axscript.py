#!/usr/bin/env python3
"""
Test AXScript parser functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripting.axscript_interpreter import AXScriptInterpreter

def test_simple_script():
    """Test simple AXScript execution"""
    interpreter = AXScriptInterpreter()
    
    # Simple test script
    test_script = """
var x = 10;
var y = 20;
var result = x + y;
print("Result: " + result);
"""
    
    print("Testing simple script...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Simple script executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Simple script failed:", result["error"])
    
    return result["success"]

def test_function_script():
    """Test function definition and calling"""
    interpreter = AXScriptInterpreter()
    
    # Function test script
    test_script = """
function add(a, b) {
    return a + b;
}

var result = add(5, 3);
print("Function result: " + result);
"""
    
    print("\nTesting function script...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Function script executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Function script failed:", result["error"])
    
    return result["success"]

def test_if_statement():
    """Test if statement parsing"""
    interpreter = AXScriptInterpreter()
    
    # If statement test
    test_script = """
var x = 10;
if (x > 5) {
    print("x is greater than 5");
} else {
    print("x is not greater than 5");
}
"""
    
    print("\nTesting if statement...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ If statement executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ If statement failed:", result["error"])
    
    return result["success"]

def main():
    """Run all tests"""
    print("=== AXScript Parser Tests ===\n")
    
    tests = [
        test_simple_script,
        test_function_script,
        test_if_statement
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("All tests passed! AXScript parser is working correctly.")
    else:
        print("Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()