"""
Quick Test - Hybrid Intelligence System
======================================
"""

try:
    import flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import error: {e}")

try:
    from flask_cors import CORS
    print("✅ Flask-CORS imported successfully")
except ImportError as e:
    print(f"❌ Flask-CORS import error: {e}")

try:
    import requests
    print("✅ Requests imported successfully")
except ImportError as e:
    print(f"❌ Requests import error: {e}")

try:
    from hybrid_intelligence_rag_system import HybridIntelligenceRAGSystem
    print("✅ Hybrid Intelligence system imported successfully")
    
    # Quick test
    system = HybridIntelligenceRAGSystem()
    print("✅ Hybrid Intelligence system initialized")
    
except ImportError as e:
    print(f"❌ Hybrid Intelligence import error: {e}")
except Exception as e:
    print(f"❌ Hybrid Intelligence initialization error: {e}")

print("\n🔧 System Status:")
print("Ready to start Flask backend!" if all([
    'flask' in locals(),
    'CORS' in locals() if 'flask_cors' in str(locals()) else False,
    'requests' in locals(),
    'HybridIntelligenceRAGSystem' in locals()
]) else "Dependencies need attention")