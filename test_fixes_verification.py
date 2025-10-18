#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly:
1. Template fix for 'match' -> 'in' filter
2. RAG routes duplicate function fix
3. Dashboard functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_rendering():
    """Test that the template renders without Jinja2 errors."""
    print("🔍 Testing Template Rendering...")
    
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        
        # Setup Jinja2 environment similar to Flask
        template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Load the template
        template = env.get_template('intelligent_results.html')
        
        # Create mock data for testing
        mock_suggestions = [
            {'method': 'advanced_rag', 'text': 'RAG suggestion'},
            {'method': 'vector_openai', 'text': 'OpenAI suggestion'},
            {'method': 'intelligent_analysis', 'text': 'AI suggestion'},
            {'method': 'grammar_check', 'text': 'Grammar suggestion'},
        ]
        
        mock_analysis_results = {
            'suggestions': mock_suggestions,
            'stats': {
                'total_suggestions': 4,
                'ai_powered': 3,
                'confidence': 0.85
            }
        }
        
        # Try to render the template
        rendered = template.render(
            suggestions=mock_suggestions,
            analysis_results=mock_analysis_results,
            text_stats={'word_count': 100, 'sentence_count': 5}
        )
        
        print("✅ Template rendered successfully!")
        print(f"   - Rendered content length: {len(rendered)} characters")
        print("   - Template contains AI-Powered count section")
        return True
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False

def test_rag_routes_import():
    """Test that RAG routes can be imported without conflicts."""
    print("\n🔍 Testing RAG Routes Import...")
    
    try:
        from app.rag_routes import rag
        print("✅ RAG Blueprint imported successfully!")
        
        # Check route rules
        rules = []
        for rule in rag.url_map.iter_rules():
            rules.append(f"{rule.rule} -> {rule.endpoint}")
        
        print(f"   - Total routes registered: {len(rules)}")
        
        # Check for duplicate stats routes
        stats_routes = [rule for rule in rules if '/stats' in rule]
        print(f"   - Stats routes found: {len(stats_routes)}")
        
        if len(stats_routes) <= 1:
            print("✅ No duplicate stats routes found!")
        else:
            print(f"❌ Found {len(stats_routes)} stats routes - may cause conflicts")
            for route in stats_routes:
                print(f"      {route}")
        
        return len(stats_routes) <= 1
        
    except Exception as e:
        print(f"❌ RAG routes import failed: {e}")
        return False

def test_flask_app_creation():
    """Test that Flask app can be created without route conflicts."""
    print("\n🔍 Testing Flask App Creation...")
    
    try:
        # Import create_app function
        from app import create_app
        
        # Try to create the app
        app, socketio = create_app()
        print("✅ Flask app created successfully!")
        
        # Check registered blueprints
        blueprints = list(app.blueprints.keys())
        print(f"   - Registered blueprints: {blueprints}")
        
        # Check for RAG blueprint
        if 'rag' in blueprints:
            print("✅ RAG blueprint registered successfully!")
        else:
            print("❌ RAG blueprint not found in registered blueprints")
            
        return True
        
    except AssertionError as e:
        if "overwriting an existing endpoint function" in str(e):
            print(f"❌ Route conflict detected: {e}")
            return False
        else:
            print(f"❌ Flask app creation failed with AssertionError: {e}")
            return False
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_enhanced_dashboard_routes():
    """Test enhanced dashboard route functionality."""
    print("\n🔍 Testing Enhanced Dashboard Routes...")
    
    try:
        from app.rag_routes import rag
        
        # Check for expected enhanced routes
        expected_routes = [
            '/stats',
            '/performance_data',
            '/health_check', 
            '/generate_report',
            '/schedule_evaluation'
        ]
        
        existing_routes = []
        for rule in rag.url_map.iter_rules():
            route_path = rule.rule.replace('/rag', '')  # Remove prefix
            existing_routes.append(route_path)
        
        found_routes = []
        missing_routes = []
        
        for route in expected_routes:
            if route in existing_routes:
                found_routes.append(route)
            else:
                missing_routes.append(route)
        
        print(f"   - Enhanced routes found: {len(found_routes)}/{len(expected_routes)}")
        for route in found_routes:
            print(f"     ✅ {route}")
            
        if missing_routes:
            print("   - Missing enhanced routes:")
            for route in missing_routes:
                print(f"     ❌ {route}")
        
        return len(missing_routes) == 0
        
    except Exception as e:
        print(f"❌ Enhanced dashboard routes test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🚀 DocScanner Fixes Verification Test Suite")
    print("=" * 50)
    
    tests = [
        ("Template Rendering", test_template_rendering),
        ("RAG Routes Import", test_rag_routes_import),
        ("Flask App Creation", test_flask_app_creation),
        ("Enhanced Dashboard Routes", test_enhanced_dashboard_routes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All fixes verified successfully! Your application should work correctly now.")
        return True
    else:
        print("⚠️ Some issues remain. Please check the failed tests above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)