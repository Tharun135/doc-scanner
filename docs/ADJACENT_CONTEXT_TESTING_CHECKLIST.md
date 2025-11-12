# Testing Checklist: Adjacent Context Enhancement

## ✅ Pre-Testing Setup

- [ ] Ensure the application is running
- [ ] Verify Ollama is running (if using local AI)
- [ ] Check that hybrid intelligence is available (optional)

## 🧪 Test Scenarios

### Test 1: Requirement Context (Your Original Issue)

**Document Content:**
```
Prerequisites

The following requirement must be met:
Access to the IED on which the IE app is installed.
```

**Steps:**
1. Upload the document
2. Wait for analysis to complete
3. Click on sentence "Access to the IED on which the IE app is installed."
4. Click "Get AI Suggestion" for passive voice issue

**Expected Result:**
- ✅ AI suggestion: "You must have access to the IED on which the IE app is installed."
- ✅ Maintains requirement format (not converted to description)
- ✅ Uses "must" to indicate requirement
- ✅ Explanation mentions understanding requirement context

**Actual Result:**
- [ ] Suggestion: _______________________________________________
- [ ] Maintains requirement format: Yes / No
- [ ] Quality: Excellent / Good / Poor

---

### Test 2: Step-by-Step Instructions

**Document Content:**
```
Configuration Steps

Follow these steps to configure the system:
The settings are saved to the configuration file.
Click the Apply button to finalize changes.
```

**Steps:**
1. Upload the document
2. Click on sentence "The settings are saved to the configuration file."
3. Request AI suggestion for passive voice

**Expected Result:**
- ✅ AI suggestion: "Save the settings to the configuration file."
- ✅ Uses imperative form (command)
- ✅ Matches the style of surrounding instructions

**Actual Result:**
- [ ] Suggestion: _______________________________________________
- [ ] Uses imperative form: Yes / No
- [ ] Quality: Excellent / Good / Poor

---

### Test 3: System Description

**Document Content:**
```
System Overview

The system operates as follows:
Data is displayed in the dashboard.
Users can view real-time metrics.
```

**Steps:**
1. Upload the document
2. Click on sentence "Data is displayed in the dashboard."
3. Request AI suggestion for passive voice

**Expected Result:**
- ✅ AI suggestion: "The system displays data in the dashboard."
- ✅ Uses "system" as subject (not "you")
- ✅ Maintains descriptive tone

**Actual Result:**
- [ ] Suggestion: _______________________________________________
- [ ] Uses system as subject: Yes / No
- [ ] Quality: Excellent / Good / Poor

---

### Test 4: User Action Context

**Document Content:**
```
User Tasks

To complete the setup:
The configuration file is edited manually.
The application is restarted.
```

**Steps:**
1. Upload the document
2. Click on sentence "The configuration file is edited manually."
3. Request AI suggestion for passive voice

**Expected Result:**
- ✅ AI suggestion: "Edit the configuration file manually." or "You edit the configuration file manually."
- ✅ Appropriate for user action context
- ✅ Uses imperative or second person

**Actual Result:**
- [ ] Suggestion: _______________________________________________
- [ ] Appropriate form: Yes / No
- [ ] Quality: Excellent / Good / Poor

---

### Test 5: Long Sentence with Context

**Document Content:**
```
Installation Process

Before you begin installation:
The system configuration must be validated and all prerequisites must be met and the network connectivity must be tested before proceeding with the installation process.
After validation is complete:
```

**Steps:**
1. Upload the document
2. Click on the long sentence
3. Request AI suggestion for long sentence

**Expected Result:**
- ✅ Splits into 2-3 shorter sentences
- ✅ Maintains requirement/prerequisite tone from "Before you begin"
- ✅ Keeps logical flow with adjacent sentences
- ✅ Uses appropriate transition words

**Actual Result:**
- [ ] Suggestion: _______________________________________________
- [ ] Maintains context: Yes / No
- [ ] Quality: Excellent / Good / Poor

---

### Test 6: Mixed Context

**Document Content:**
```
Requirements
The following requirements must be met:

Access to the development environment is provided.
Source code is downloaded from the repository.
Dependencies are installed using npm install.

Steps
1. Open the terminal
2. Navigate to the project directory
```

**Steps:**
1. Upload the document
2. Test each passive voice sentence
3. Compare suggestions for requirement vs. step context

**Expected Results:**
- ✅ Requirement sentences maintain "must" format
- ✅ Step context uses imperative form
- ✅ Different treatment based on section context

**Actual Results:**
- [ ] Requirement 1: _______________________________________________
- [ ] Requirement 2: _______________________________________________
- [ ] Requirement 3: _______________________________________________
- [ ] Context awareness: Yes / No

---

## 🔍 Additional Checks

### Check 1: No Adjacent Sentences (Edge Case)
**Test:** First sentence in document with no previous sentence
- [ ] AI still provides valid suggestion: Yes / No
- [ ] No errors or crashes: Yes / No

### Check 2: Last Sentence (Edge Case)
**Test:** Last sentence in document with no next sentence
- [ ] AI still provides valid suggestion: Yes / No
- [ ] No errors or crashes: Yes / No

### Check 3: Single Sentence Document
**Test:** Document with only one sentence
- [ ] AI handles gracefully: Yes / No
- [ ] Provides reasonable suggestion: Yes / No

---

## 📊 Overall Assessment

### Quality Metrics
- [ ] AI suggestions are contextually appropriate: ___/6 tests passed
- [ ] Maintains sentence type (requirement/instruction/description): ___/6 tests passed
- [ ] No errors or crashes: ___/6 tests passed
- [ ] Response time is acceptable (< 10 seconds): Yes / No

### Improvements Observed
- [ ] Better requirement handling vs. before
- [ ] More appropriate subject selection (you/system/imperative)
- [ ] Suggestions fit document flow better
- [ ] Fewer awkward or incorrect conversions

### Issues Found
- [ ] None
- [ ] Minor issues: _______________________________________________
- [ ] Major issues: _______________________________________________

---

## 📝 Notes

**Testing Date:** _______________

**Tester:** _______________

**Environment:**
- Python Version: _______________
- OS: _______________
- AI System: Ollama / OpenAI / Hybrid

**Additional Comments:**
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________

---

## ✅ Final Checklist

- [ ] All test scenarios completed
- [ ] Edge cases tested
- [ ] Overall quality improvement confirmed
- [ ] No regressions or new bugs
- [ ] Ready for production use

**Status:** 
- [ ] ✅ PASS - Ready to use
- [ ] ⚠️ PASS with minor issues - Document issues
- [ ] ❌ FAIL - Needs fixes

---

## 🎯 Success Criteria

**This feature is successful if:**
1. ✅ AI suggestions consider adjacent sentence context
2. ✅ Requirements are maintained as requirements (not converted to descriptions)
3. ✅ Instructions use imperative form appropriately
4. ✅ Descriptions use appropriate subjects (system vs. user)
5. ✅ No decrease in overall suggestion quality
6. ✅ No new errors or crashes

**Target:** Pass 5/6 success criteria

**Actual:** ___/6 passed
