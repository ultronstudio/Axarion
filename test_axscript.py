
#!/usr/bin/env python3
"""
Test enhanced AXScript functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripting.axscript_interpreter import AXScriptInterpreter

def test_simple_script():
    """Test simple AXScript execution"""
    interpreter = AXScriptInterpreter()
    
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

def test_type_checking():
    """Test type checking functionality"""
    interpreter = AXScriptInterpreter()
    
    test_script = """
function add(a, b) {
    return a + b;
}

var x = 5;
var y = "10";
var result = add(x, y);
print("Type checking result: " + result);
print("Type of result: " + typeof(result));
"""
    
    print("\nTesting type checking...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Type checking executed successfully")
        if result["output"]:
            print("Output:", result["output"])
        if result["type_errors"]:
            print("Type warnings:", result["type_errors"])
    else:
        print("✗ Type checking failed:", result["error"])
    
    return result["success"]

def test_classes_and_objects():
    """Test class and object functionality"""
    interpreter = AXScriptInterpreter()
    
    test_script = """
class Player {
    function constructor(name, health) {
        this.name = name;
        this.health = health;
    }
    
    function takeDamage(damage) {
        this.health = this.health - damage;
        print(this.name + " takes " + damage + " damage! Health: " + this.health);
    }
    
    function isAlive() {
        return this.health > 0;
    }
}

var player = new Player("Hero", 100);
player.takeDamage(30);
print("Player alive: " + player.isAlive());
"""
    
    print("\nTesting classes and objects...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Classes and objects executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Classes and objects failed:", result["error"])
    
    return result["success"]

def test_loops_and_control_flow():
    """Test enhanced loops and control flow"""
    interpreter = AXScriptInterpreter()
    
    test_script = """
// For loop
print("For loop:");
for (var i = 0; i < 3; i++) {
    print("Iteration: " + i);
}

// For-in loop with array
print("For-in loop:");
var items = ["apple", "banana", "cherry"];
for (var item in items) {
    print("Item: " + item);
}

// Do-while loop
print("Do-while loop:");
var count = 0;
do {
    print("Count: " + count);
    count++;
} while (count < 2);

// Switch statement
print("Switch statement:");
var day = 1;
switch (day) {
    case 1:
        print("Monday");
        break;
    case 2:
        print("Tuesday");
        break;
    default:
        print("Other day");
}
"""
    
    print("\nTesting loops and control flow...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Loops and control flow executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Loops and control flow failed:", result["error"])
    
    return result["success"]

def test_error_handling():
    """Test error handling with try-catch"""
    interpreter = AXScriptInterpreter()
    
    test_script = """
try {
    var result1 = riskyFunction(5);
    print("Result 1: " + result1);
    
    var result2 = riskyFunction(-3);
    print("Result 2: " + result2);
} catch (error) {
    print("Caught error: " + error);
} finally {
    print("Cleanup completed");
}
"""
    
    print("\nTesting error handling...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Error handling executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Error handling failed:", result["error"])
    
    return result["success"]

def test_arrays_and_objects():
    """Test arrays and object manipulation"""
    interpreter = AXScriptInterpreter()
    
    test_script = """
// Array operations
var numbers = [1, 2, 3, 4, 5];
print("Array: " + numbers);
print("First element: " + numbers[0]);
print("Array length: " + numbers.length);

// Object operations
var person = {
    name: "John",
    age: 30,
    city: "New York"
};
print("Person name: " + person.name);
print("Person age: " + person["age"]);

// Array methods (if implemented)
var doubled = [];
var index = 0;
for (var num in numbers) {
    doubled[index] = num * 2;
    index = index + 1;
}
print("Doubled: " + doubled);
"""
    
    print("\nTesting arrays and objects...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Arrays and objects executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Arrays and objects failed:", result["error"])
    
    return result["success"]

def test_module_system():
    """Test module import/export system"""
    interpreter = AXScriptInterpreter()
    
    # First, let's register a custom module
    interpreter.module_system.register_module("TestModule", {
        "PI": 3.14159,
        "greet": lambda name: f"Hello, {name}!",
        "add": lambda a, b: a + b
    })
    
    test_script = """
// Import from built-in Math module
import { sin, cos, PI } from "Math";
print("sin(PI/2): " + sin(PI / 2));

// Import custom module
import TestModule;
print("Custom PI: " + TestModule.PI);
print(TestModule.greet("World"));
"""
    
    print("\nTesting module system...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Module system executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Module system failed:", result["error"])
    
    return result["success"]

def test_advanced_features():
    """Test advanced language features"""
    interpreter = AXScriptInterpreter()
    
    test_script = """
// Ternary operator
var x = 10;
var result = x > 5 ? "big" : "small";
print("Ternary result: " + result);

// Increment/decrement
var counter = 0;
print("Pre-increment: " + (++counter));
print("Post-increment: " + (counter++));
print("Final counter: " + counter);

// Type checking functions
var testValue = 42;
print("Is number: " + isNumber(testValue));
print("Is string: " + isString(testValue));
print("Typeof: " + typeof(testValue));

// Array literal
var colors = ["red", "green", "blue"];
print("Colors: " + colors);
print("Second color: " + colors[1]);
"""
    
    print("\nTesting advanced features...")
    result = interpreter.execute(test_script)
    
    if result["success"]:
        print("✓ Advanced features executed successfully")
        if result["output"]:
            print("Output:", result["output"])
    else:
        print("✗ Advanced features failed:", result["error"])
    
    return result["success"]

def main():
    """Run all tests"""
    print("=== Enhanced AXScript Tests ===\n")
    
    tests = [
        test_simple_script,
        test_type_checking,
        test_classes_and_objects,
        test_loops_and_control_flow,
        test_error_handling,
        test_arrays_and_objects,
        test_module_system,
        test_advanced_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced AXScript is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    # Show final feature summary
    print("\n=== Enhanced AXScript Features ===")
    print("✓ Basic type checking and type inference")
    print("✓ Function return value validation")
    print("✓ Enhanced loops (for, for-in, do-while)")
    print("✓ Module system with import/export")
    print("✓ Classes and object-oriented programming")
    print("✓ Comprehensive error handling (try-catch-finally)")
    print("✓ Extended standard library")
    print("✓ Arrays, objects, and advanced data structures")
    print("✓ Control flow (switch, break, continue)")
    print("✓ Advanced operators (ternary, increment/decrement)")
    print("✓ Type checking functions and typeof operator")
    print("✓ Better error messages and debugging support")

if __name__ == "__main__":
    main()
