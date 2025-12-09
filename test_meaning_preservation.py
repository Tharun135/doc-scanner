"""
Comprehensive meaning preservation test.
Tests semantic context + rewrite safety on realistic technical document.
"""

import sys
sys.path.insert(0, 'D:\\doc-scanner')

def test_comprehensive_document():
    """
    Test a realistic technical document with:
    - Repeated acronyms
    - UI labels  
    - Pronouns
    - List steps
    - Technical causality
    """
    
    from app.semantic_context import build_document_context
    from app.document_first_ai import DocumentFirstAIEngine
    
    # Realistic technical documentation
    sentences = [
        # Introduction with acronym expansion
        "The Programmable Logic Controller (PLC) manages industrial automation.",
        
        # Pronoun reference to PLC
        "It connects to multiple sensors and actuators.",
        
        # Repeated acronym (should NOT expand again)
        "Each PLC monitors real-time data streams.",
        
        # UI label reference
        "You configure the PLC through the Control Panel interface.",
        
        # Another pronoun (ambiguous - could be PLC or Control Panel)
        "It displays connection status and error codes.",
        
        # List step 1
        "First, you open the Configuration menu.",
        
        # List step 2  
        "Next, you select Network Settings from the dropdown.",
        
        # List step 3
        "Then you enter the IP address in the Address field.",
        
        # Technical process with causality
        "The controller validates the configuration before applying changes.",
        
        # Pronoun chain
        "It then restarts the network service.",
        
        # Expected outcome
        "This re-establishes communication with connected devices.",
        
        # Error condition
        "If validation fails, the system displays an error message.",
        
        # Another acronym (new)
        "The Human Machine Interface (HMI) shows diagnostic data.",
        
        # Repeated HMI
        "Operators monitor HMI alerts during operation.",
        
        # Final status check
        "The Status LED indicates whether the connection is active."
    ]
    
    print("=" * 80)
    print("COMPREHENSIVE MEANING PRESERVATION TEST")
    print("=" * 80)
    print(f"\nTest document: {len(sentences)} sentences")
    print("\nBuilding semantic context...")
    
    # Build context
    sections = {
        0: "Introduction",
        1: "Introduction", 
        2: "Introduction",
        3: "Configuration",
        4: "Configuration",
        5: "Configuration Steps",
        6: "Configuration Steps",
        7: "Configuration Steps",
        8: "Operation",
        9: "Operation",
        10: "Operation",
        11: "Error Handling",
        12: "Monitoring",
        13: "Monitoring",
        14: "Status"
    }
    
    ctx = build_document_context(sentences, sections, nlp=None)
    
    print(f"✅ Context built:")
    print(f"   - Entities: {len(ctx.entities)}")
    print(f"   - Acronyms: {len(ctx.acronyms)}")
    print(f"   - Pronoun links: {len(ctx.pronoun_links)}")
    
    # Show acronym tracking
    print(f"\n📝 Acronyms detected:")
    for acro, info in ctx.acronyms.items():
        print(f"   - {acro}: expanded at sentence {info['first']}, used {len(info['all_uses'])} times")
    
    # Show pronoun links
    print(f"\n🔗 Pronoun links:")
    for idx, links in ctx.pronoun_links.items():
        print(f"   - Sentence {idx}: {links}")
    
    # Now test AI suggestions on problematic sentences
    engine = DocumentFirstAIEngine()
    
    test_cases = [
        {
            "index": 1,
            "issue": "Contains pronoun 'It' - should resolve to 'PLC'",
            "feedback": "Replace pronoun with explicit subject"
        },
        {
            "index": 4,
            "issue": "Ambiguous pronoun 'It' - could be PLC or Control Panel",
            "feedback": "Clarify pronoun reference"
        },
        {
            "index": 9,
            "issue": "Pronoun 'It' after controller - should resolve",
            "feedback": "Replace pronoun with subject"
        },
        {
            "index": 10,
            "issue": "Pronoun 'This' - should reference previous action",
            "feedback": "Clarify demonstrative pronoun"
        },
        {
            "index": 2,
            "issue": "Contains acronym PLC - should NOT expand (already expanded at sentence 0)",
            "feedback": "Check clarity"
        },
        {
            "index": 13,
            "issue": "Contains acronym HMI - should NOT expand (already expanded at sentence 12)",
            "feedback": "Check clarity"
        }
    ]
    
    print("\n" + "=" * 80)
    print("TESTING AI SUGGESTIONS")
    print("=" * 80)
    
    results = {
        "blocked": 0,
        "allowed": 0,
        "unchanged": 0,
        "false_blocks": [],
        "false_rewrites": [],
        "good_rewrites": []
    }
    
    for test_case in test_cases:
        idx = test_case["index"]
        original = sentences[idx]
        
        print(f"\n{'─' * 80}")
        print(f"Test Case {idx}: {test_case['issue']}")
        print(f"{'─' * 80}")
        print(f"Original: {original}")
        print(f"Section: {sections.get(idx, 'Unknown')}")
        
        try:
            result = engine.generate_document_first_suggestion(
                feedback_text=test_case["feedback"],
                sentence_context=original,
                document_type="technical",
                sentence_index=idx,
                document_context=ctx,
                issue_type="pronoun_clarity"
            )
            
            suggestion = result.get("suggestion", "")
            method = result.get("method", "")
            
            print(f"Suggestion: {suggestion}")
            print(f"Method: {method}")
            
            # Analyze result
            if method == "meaning_preservation_override":
                results["blocked"] += 1
                print("🛡️ BLOCKED by safety check")
                
                # Check if this was a false block (suggestion was actually fine)
                if suggestion == original and "pronoun" in test_case["issue"].lower():
                    results["false_blocks"].append({
                        "index": idx,
                        "original": original,
                        "reason": "Should have resolved pronoun but was blocked"
                    })
                    print("⚠️ Potential FALSE BLOCK - pronoun should have been resolved")
                    
            elif suggestion == original:
                results["unchanged"] += 1
                print("➡️ UNCHANGED (original preserved)")
                
            else:
                results["allowed"] += 1
                print("✅ REWRITE ALLOWED")
                
                # Check if meaning was preserved
                original_lower = original.lower()
                suggestion_lower = suggestion.lower()
                
                # Check for bad rewrites
                issues = []
                
                # Check 1: Pronoun should be resolved
                if any(p in original_lower for p in [' it ', ' this ', ' that ']):
                    if any(p in suggestion_lower for p in [' it ', ' this ', ' that ']):
                        issues.append("Pronoun still present (not resolved)")
                
                # Check 2: Acronym should not be re-expanded
                if "plc" in original_lower and "programmable logic controller" in suggestion_lower:
                    issues.append("Acronym re-expanded (should stay as PLC)")
                    
                if "hmi" in original_lower and "human machine interface" in suggestion_lower:
                    issues.append("Acronym re-expanded (should stay as HMI)")
                
                # Check 3: Temporal markers preserved
                temporal = ['first', 'next', 'then', 'after', 'before']
                for marker in temporal:
                    if marker in original_lower and marker not in suggestion_lower:
                        issues.append(f"Temporal marker '{marker}' lost")
                
                # Check 4: No merge/condense
                if len(suggestion.split()) < len(original.split()) * 0.7:
                    issues.append("Sentence condensed too much (possible meaning loss)")
                
                if issues:
                    results["false_rewrites"].append({
                        "index": idx,
                        "original": original,
                        "suggestion": suggestion,
                        "issues": issues
                    })
                    print(f"❌ FALSE REWRITE DETECTED:")
                    for issue in issues:
                        print(f"   - {issue}")
                else:
                    results["good_rewrites"].append({
                        "index": idx,
                        "original": original,
                        "suggestion": suggestion
                    })
                    print("✅ Good rewrite (meaning preserved)")
                    
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    total = results["blocked"] + results["allowed"] + results["unchanged"]
    
    print(f"\nTotal test cases: {total}")
    print(f"  🛡️  Blocked by safety: {results['blocked']}")
    print(f"  ✅ Rewrites allowed: {results['allowed']}")
    print(f"  ➡️  Unchanged: {results['unchanged']}")
    
    print(f"\nQuality metrics:")
    print(f"  ✅ Good rewrites: {len(results['good_rewrites'])}")
    print(f"  ❌ False rewrites (allowed but wrong): {len(results['false_rewrites'])}")
    print(f"  ⚠️  False blocks (blocked but was ok): {len(results['false_blocks'])}")
    
    if results["false_rewrites"]:
        print(f"\n❌ FALSE REWRITES FOUND:")
        for fr in results["false_rewrites"]:
            print(f"\n  Sentence {fr['index']}:")
            print(f"    Original: {fr['original']}")
            print(f"    Bad suggestion: {fr['suggestion']}")
            print(f"    Issues:")
            for issue in fr['issues']:
                print(f"      - {issue}")
    
    if results["false_blocks"]:
        print(f"\n⚠️ FALSE BLOCKS FOUND:")
        for fb in results["false_blocks"]:
            print(f"\n  Sentence {fb['index']}:")
            print(f"    Original: {fb['original']}")
            print(f"    Reason: {fb['reason']}")
    
    # Calculate success rate
    successful = len(results['good_rewrites']) + results['unchanged'] + results['blocked']
    failures = len(results['false_rewrites']) + len(results['false_blocks'])
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    print(f"\n" + "=" * 80)
    print(f"OVERALL SUCCESS RATE: {success_rate:.1f}%")
    print(f"  ✅ Successful operations: {successful}/{total}")
    print(f"  ❌ Failures: {failures}/{total}")
    print("=" * 80)
    
    # Pass/fail criteria
    if success_rate >= 90 and len(results['false_rewrites']) == 0:
        print("\n🎉 TEST PASSED: System is safe and effective")
        return True
    elif success_rate >= 70:
        print("\n⚠️ TEST MARGINAL: System needs tuning")
        return False
    else:
        print("\n❌ TEST FAILED: System is unsafe for production")
        return False


if __name__ == "__main__":
    test_comprehensive_document()
