# Rule Index - Traceability to Style Guide

**Purpose**: Map each rule to its source section in the style guide.  
**NOT a runtime dependency** - governance only.

## Current Status
- **Total Rules**: 27 atomic JSON rules
- **Severity Levels**: 🔴 Error | 🟡 Warning | 🔵 Info
- **Test Coverage**: 100%

---

## Tense Rules (2)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| TENSE_001 | 🔴 Error | 1.2: Simple Present | Future tense prohibited in procedures |
| TENSE_002 | 🟡 Warning | 1.2: Modal Verbs | Modal verbs weaken clarity |

---

## UI Label Rules (2)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| UI_001 | 🔴 Error | 4.1: Button Phrasing | No articles or "button" with UI labels |
| UI_002 | 🔴 Error | 4.1: Button Phrasing | No "on" after action verbs |

---

## Safety Rules (2)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| SAFETY_001 | 🔴 Error | 2.1: Notice Symbols | NOTICE must not contain safety symbols |
| SAFETY_002 | 🔴 Error | 2.2: Symbol Placement | Symbol must precede DANGER/WARNING/CAUTION |

---

## Voice Rules (3)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| PERSON_001 | 🔴 Error | 3.1: Pronouns | Personal pronouns prohibited |
| IMP_001 | 🟡 Warning | 3.2: Imperative | Prefer imperative mood |
| PASSIVE_001 | 🟡 Warning | 3.3: Passive Voice | Avoid passive constructions |

---

## Clarity Rules (4)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| ADV_001 | 🟡 Warning | 9.2: Adverbs | Blacklisted adverbs |
| VAGUE_001 | 🟡 Warning | 9.3: Vague Terms | Ambiguous language |
| ARTICLE_001 | 🟡 Warning | 9.1: Articles | Unnecessary articles |
| JARGON_001 | 🔵 Info | 9.4: Jargon | Corporate speak |

---

## Grammar Rules (3)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| OXFORD_001 | 🟡 Warning | 1.5: Oxford Comma | Missing Oxford comma |
| CONTRACT_001 | 🟡 Warning | 1.6: Contractions | Contractions prohibited |
| PLURAL_001 | 🟡 Warning | 1.7: Plurals | Irregular plural forms |

---

## Procedure Rules (4)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| PROC_001 | 🟡 Warning | 5.1: Multiple Actions | Two actions in one step |
| COND_001 | 🟡 Warning | 5.2: Conditionals | "If...then" structure required |
| LIST_001 | 🟡 Warning | 5.3: Step Fusion | "then...and" pattern detected |
| LIST_002 | 🔴 Error | 5.4: Heading Format | Colon before numbered steps |

---

## Table Rules (2) ⭐ NEW

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| TABLE_001 | 🔴 Error | 6.1: Empty Cells | Empty table cells block translation |
| TABLE_002 | 🟡 Warning | 6.2: Merged Cells | Colspan/rowspan harm exports |

---

## Translation Rules (3) ⭐ NEW

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| PVERB_001 | 🟡 Warning | 7.1: Phrasal Verbs | Phrasal verbs resist translation |
| TRANS_001 | 🟡 Warning | 7.2: Idioms | Idioms harm localization |
| TRANS_002 | 🔵 Info | 7.3: Ambiguity | Vague quantities ("multiple", "various") |

---

## Consistency Rules (1) ⭐ NEW

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| CONSIST_001 | 🔴 Error | 8.1: UI Verb Case | Inconsistent capitalization (Click vs click) |

---

## Inclusivity Rules (1)

| Rule ID | Severity | Style Guide Section | Description |
|---------|----------|---------------------|-------------|
| GENDER_001 | 🔵 Info | 10.1: Gender Neutral | Gender-specific language |

---

## Severity Distribution

| Severity | Count | Commit Impact |
|----------|-------|---------------|
| 🔴 Error | 9 | Blocks commit |
| 🟡 Warning | 15 | Advisory only |
| 🔵 Info | 3 | Silent |
| **Total** | **27** | **Mixed (C)** |

---

## Coverage Map

| Style Guide Section | Rules | Coverage |
|---------------------|-------|----------|
| 1. Grammar Basics | 5 | ✅ Full |
| 2. Safety Notices | 2 | ✅ Full |
| 3. Voice & Person | 3 | ✅ Full |
| 4. UI Elements | 2 | ✅ Full |
| 5. Procedures | 4 | ✅ Full |
| 6. Tables | 2 | ⭐ NEW |
| 7. Translation | 3 | ⭐ NEW |
| 8. Consistency | 1 | ⭐ NEW |
| 9. Clarity | 4 | ✅ Full |
| 10. Inclusivity | 1 | ✅ Full |

---

## Expansion History

| Phase | Date | Rules Added | Total | Focus |
|-------|------|-------------|-------|-------|
| Initial | Dec 8, 2025 | 20 | 20 | Core violations |
| Phase 1 | Dec 9, 2025 | 7 | 27 | Lists, tables, translation |
| Phase 2 | TBD | +8 | 35 | Field feedback |
| Phase 3 | TBD | +7 | 42 | Advanced constraints |
| Target | TBD | +8 | 50 | Full guide coverage |

---

## Next Expansion: 35 → 42 (NOT YET)

**Wait for operational logs before adding:**
- List period consistency
- Command vs task list format
- Metadata standards
- Warning symbol sequences
- Synonym enforcement
- Ambiguity patterns
- Cross-reference format

**Discipline**: Add only after real-world violation patterns emerge.

---

## Usage Notes

### For Developers
- This file is **documentation only**
- Never parsed at runtime
- Updated manually when rules change
- Source of truth: `rules.json`

### For Rule Authors
- Find source section in style guide
- Create atomic regex
- Add to `rules.json`
- Update this index
- Write test case

### For Auditors
- Verify coverage against style guide
- Check severity alignment
- Validate test existence
- Confirm CI integration

---

**Last Updated**: December 9, 2025  
**Rule Count**: 27 (target: 35 by Q1 2026)  
**Status**: ✅ Production, observational mode
