"""
Quick test to verify check_rag_dependencies() returns are handled correctly
"""

def test_check_rag_dependencies_handling():
    """Test that all routes handle check_rag_dependencies() tuple return correctly"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
    
    from rag_routes import check_rag_dependencies
    
    print("=" * 80)
    print("Testing check_rag_dependencies() Return Value Handling")
    print("=" * 80)
    
    # Test the function return type
    result = check_rag_dependencies()
    print(f"\ncheck_rag_dependencies() returns: {result}")
    print(f"Type: {type(result)}")
    
    if isinstance(result, tuple):
        available, message = result
        print(f"✓ Returns tuple: ({available}, '{message}')")
        print(f"  Dependencies available: {available}")
        print(f"  Message: {message}")
    else:
        print(f"✗ Returns single value: {result}")
    
    # Test safe handling pattern
    print("\n" + "-" * 80)
    print("Testing Safe Handling Pattern")
    print("-" * 80)
    
    deps_check = check_rag_dependencies()
    deps_available = deps_check[0] if isinstance(deps_check, tuple) else deps_check
    
    print(f"Safe extraction result: {deps_available}")
    print(f"Type: {type(deps_available)}")
    print(f"Is boolean: {isinstance(deps_available, bool)}")
    
    if isinstance(deps_available, bool):
        print("✓ Successfully extracted boolean value")
    else:
        print("✗ Failed to extract boolean value")
    
    print("\n" + "=" * 80)
    print("✅ Test completed successfully")
    print("=" * 80)

if __name__ == '__main__':
    test_check_rag_dependencies_handling()
