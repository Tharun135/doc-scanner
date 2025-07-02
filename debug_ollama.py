#!/usr/bin/env python3
"""
Debug script to check Ollama API structure
"""

import ollama

try:
    print("Checking Ollama list structure...")
    models = ollama.list()
    print(f"Type of response: {type(models)}")
    print(f"Response attributes: {dir(models)}")
    
    if hasattr(models, 'models'):
        print(f"\nModels attribute type: {type(models.models)}")
        print(f"Number of models: {len(models.models)}")
        
        for i, model in enumerate(models.models):
            print(f"\nModel {i+1}:")
            print(f"  Type: {type(model)}")
            print(f"  Attributes: {dir(model)}")
            if hasattr(model, 'name'):
                print(f"  Name: {model.name}")
            if hasattr(model, 'model'):
                print(f"  Model: {model.model}")
    else:
        print("\nNo 'models' attribute found")
        print(f"Available attributes: {[attr for attr in dir(models) if not attr.startswith('_')]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
