"""
DocScanner AI — 27 Atomic Rule Remediation Knowledge Base
Ingest this into ChromaDB using the loader at the bottom of this file.
"""

RULE_REMEDIATIONS = [

    # ─────────────────────────────────────────
    # 1. TENSE & MOOD
    # ─────────────────────────────────────────
    {
        "id": "TENSE_001",
        "category": "Tense & Mood",
        "severity": "error",
        "rule": "Future tense is prohibited in technical documentation.",
        "why": (
            "Future tense introduces uncertainty and reduces instructional authority. "
            "Readers expect declarative, present-tense statements that describe system "
            "behavior as fact, not prediction."
        ),
        "detection_pattern": ["shall", "will", "will be", "is going to", "are going to"],
        "bad_examples": [
            "The system shall start the service.",
            "The file will be saved automatically.",
            "The dashboard will display the results."
        ],
        "good_examples": [
            "The system starts the service.",
            "The system saves the file automatically.",
            "The dashboard displays the results."
        ],
        "fix_instruction": (
            "Replace future-tense auxiliaries ('shall', 'will', 'will be', 'is going to') "
            "with simple present tense. The subject remains the same; only the verb form changes."
        ),
    },

    {
        "id": "TENSE_002",
        "category": "Tense & Mood",
        "severity": "warning",
        "rule": "Modal verbs (may, could, might, should, would) weaken clarity and must be avoided.",
        "why": (
            "Modal verbs introduce ambiguity about whether an action is mandatory, optional, "
            "or conditional. Technical documentation requires unambiguous instructions. "
            "'Should' implies suggestion; 'must' implies requirement — these are not interchangeable."
        ),
        "detection_pattern": ["may", "could", "might", "should", "would"],
        "bad_examples": [
            "You should click Save before closing.",
            "The system may restart after the update.",
            "This could cause data loss."
        ],
        "good_examples": [
            "Click Save before closing.",
            "The system restarts after the update.",
            "This causes data loss."
        ],
        "fix_instruction": (
            "Replace modal verbs with imperative mood (for instructions) or simple present tense "
            "(for system behavior). If the action is truly optional, rewrite as a NOTE admonition "
            "rather than using a modal verb inline."
        ),
    },

    # ─────────────────────────────────────────
    # 2. UI LABELING
    # ─────────────────────────────────────────
    {
        "id": "UI_001",
        "category": "UI Labeling",
        "severity": "error",
        "rule": "Do not use articles or generic nouns with UI element labels.",
        "why": (
            "Articles and generic nouns ('the Save button', 'the OK dialog') add noise and "
            "can cause translation errors. UI labels are proper nouns in technical writing "
            "and must be referenced directly without qualifiers."
        ),
        "detection_pattern": [
            "the .* button", "the .* dialog", "the .* menu", "the .* field",
            "the .* tab", "the .* checkbox", "the .* dropdown"
        ],
        "bad_examples": [
            "Click the Save button.",
            "Select the File menu.",
            "Check the Enable checkbox."
        ],
        "good_examples": [
            "Click Save.",
            "Select File.",
            "Select Enable."
        ],
        "fix_instruction": (
            "Remove the article ('the', 'a', 'an') and the generic noun ('button', 'menu', "
            "'field', 'tab', 'checkbox'). Keep only the UI label itself, formatted in bold "
            "or the project's UI element style (e.g., **Save**)."
        ),
    },

    {
        "id": "UI_002",
        "category": "UI Labeling",
        "severity": "error",
        "rule": "Do not use 'on' after action verbs that reference UI elements.",
        "why": (
            "'Click on', 'tap on', and 'press on' are redundant constructions. "
            "The preposition 'on' adds no meaning and inflates word count. "
            "Style guides from Microsoft, Apple, and Google all prohibit this pattern."
        ),
        "detection_pattern": ["click on", "tap on", "press on", "double-click on"],
        "bad_examples": [
            "Click on Save.",
            "Tap on the icon.",
            "Double-click on the file."
        ],
        "good_examples": [
            "Click Save.",
            "Tap the icon.",
            "Double-click the file."
        ],
        "fix_instruction": (
            "Delete 'on' immediately after the action verb. The sentence requires no other changes."
        ),
    },

    {
        "id": "PLURAL_001",
        "category": "UI Labeling",
        "severity": "warning",
        "rule": "Do not reference UI elements in plural without naming them explicitly.",
        "why": (
            "Plural references like 'click the buttons' are ambiguous — the reader cannot "
            "identify which specific controls are meant. Each UI element referenced must be "
            "named individually."
        ),
        "detection_pattern": ["buttons", "menus", "checkboxes", "fields", "tabs", "options"],
        "bad_examples": [
            "Click the buttons to proceed.",
            "Fill in the fields.",
            "Select one of the options."
        ],
        "good_examples": [
            "Click Save or Cancel.",
            "Enter values in Name and Description.",
            "Select Enable or Disable."
        ],
        "fix_instruction": (
            "Replace the plural generic noun with the explicit names of each UI element, "
            "separated by 'or' (for alternatives) or 'and' (for required sequence)."
        ),
    },

    # ─────────────────────────────────────────
    # 3. SAFETY STANDARDS
    # ─────────────────────────────────────────
    {
        "id": "SAFETY_001",
        "category": "Safety Standards",
        "severity": "error",
        "rule": "NOTICE blocks must not contain safety symbols. NOTICE is for property damage only.",
        "why": (
            "The ANSI Z535 and IEC 82079 safety standards define strict admonition levels. "
            "NOTICE covers property damage or data loss — not personal injury. "
            "Including a ⚠️ symbol inside a NOTICE block misleads readers into treating "
            "property-level risks as personal-safety hazards."
        ),
        "detection_pattern": ["NOTICE", "⚠️", "warning symbol in notice"],
        "bad_examples": [
            "NOTICE ⚠️: Improper shutdown may corrupt the database.",
            "NOTICE: ⚠️ Do not remove the device while updating."
        ],
        "good_examples": [
            "NOTICE: Improper shutdown may corrupt the database.",
            "NOTICE: Do not remove the device while updating."
        ],
        "fix_instruction": (
            "Remove the safety symbol from the NOTICE block entirely. "
            "If the hazard involves personal injury risk, upgrade the admonition level to "
            "CAUTION, WARNING, or DANGER and retain the symbol there."
        ),
    },

    {
        "id": "SAFETY_002",
        "category": "Safety Standards",
        "severity": "error",
        "rule": "WARNING, DANGER, and CAUTION blocks must include a leading safety symbol (⚠️).",
        "why": (
            "Per ANSI Z535.6 and ISO 11684, personal-safety admonitions must be visually "
            "distinguishable from informational notes. The safety symbol is not decorative — "
            "it is a required signal word element that ensures readers identify life-safety content."
        ),
        "detection_pattern": ["WARNING:", "DANGER:", "CAUTION:"],
        "bad_examples": [
            "WARNING: High voltage present. Do not open the enclosure.",
            "CAUTION: Hot surface. Allow to cool before handling."
        ],
        "good_examples": [
            "⚠️ WARNING: High voltage present. Do not open the enclosure.",
            "⚠️ CAUTION: Hot surface. Allow to cool before handling."
        ],
        "fix_instruction": (
            "Prepend the ⚠️ symbol (or the project's approved safety icon) immediately before "
            "the signal word (WARNING / DANGER / CAUTION). Ensure a space separates the symbol "
            "from the signal word."
        ),
    },

    # ─────────────────────────────────────────
    # 4. VOICE & PERSON
    # ─────────────────────────────────────────
    {
        "id": "PERSON_001",
        "category": "Voice & Person",
        "severity": "error",
        "rule": "First-person singular pronouns (I, my, me) are prohibited in technical documentation.",
        "why": (
            "Technical documentation is institutional, not personal. First-person singular "
            "implies authorship and opinion, undermining the objective, authoritative tone "
            "required. It also creates translation inconsistencies across locales."
        ),
        "detection_pattern": ["\\bI\\b", "\\bmy\\b", "\\bme\\b", "\\bI've\\b", "\\bI'm\\b"],
        "bad_examples": [
            "I recommend saving your work frequently.",
            "In my experience, this setting works best.",
            "Contact me if the issue persists."
        ],
        "good_examples": [
            "Save work frequently.",
            "This setting produces optimal results.",
            "Contact support if the issue persists."
        ],
        "fix_instruction": (
            "Rewrite in second person (you/your) for user-directed instructions, or use "
            "passive/impersonal constructions for general statements. "
            "Remove the first-person pronoun and restructure the sentence."
        ),
    },

    {
        "id": "IMPERATIVE_001",
        "category": "Voice & Person",
        "severity": "error",
        "rule": "Procedural steps must begin with an action verb in imperative mood.",
        "why": (
            "Numbered steps in procedures must start with a verb so the reader immediately "
            "knows what action to take. Non-imperative openings (e.g., 'The next step is…', "
            "'You need to…') bury the action and slow comprehension."
        ),
        "detection_pattern": [
            "^The next step", "^You need to", "^You should", "^Now you", "^In this step"
        ],
        "bad_examples": [
            "The next step is to click Save.",
            "You need to enter your credentials.",
            "Now you should restart the service."
        ],
        "good_examples": [
            "Click Save.",
            "Enter your credentials.",
            "Restart the service."
        ],
        "fix_instruction": (
            "Delete the preamble and open the step directly with the action verb. "
            "Use base verb form (Click, Enter, Restart) with no subject."
        ),
    },

    {
        "id": "PASSIVE_001",
        "category": "Voice & Person",
        "severity": "warning",
        "rule": "Passive voice obscures the actor and must be rewritten in active voice.",
        "why": (
            "Passive voice hides who performs an action, creating ambiguity in instructions. "
            "'The file is saved' — by whom? The system? The user? Active voice eliminates "
            "this ambiguity and produces shorter, clearer sentences."
        ),
        "detection_pattern": [
            "is saved", "is updated", "is displayed", "is generated",
            "was created", "are shown", "will be processed"
        ],
        "bad_examples": [
            "The file is saved to the output folder.",
            "An error message is displayed.",
            "The report is generated automatically."
        ],
        "good_examples": [
            "The system saves the file to the output folder.",
            "The system displays an error message.",
            "The system generates the report automatically."
        ],
        "fix_instruction": (
            "Identify the specific product, component, or actor (e.g., IEM, user, application) from the context of the sentence and make it the subject. "
            "Convert the passive verb phrase ('is saved') to active ('saves'). "
            "Avoid generic terms like 'The system' if the actual software name or component is mentioned in the sentence. "
            "If the actor is genuinely unknown, passive voice is acceptable — document the exception."
        ),
    },

    # ─────────────────────────────────────────
    # 5. CLARITY & PRECISION
    # ─────────────────────────────────────────
    {
        "id": "ADV_001",
        "category": "Clarity & Precision",
        "severity": "warning",
        "rule": "Precision-reducing adverbs (simply, easily, quickly, basically, very) are prohibited.",
        "why": (
            "These adverbs are subjective and condescending. What is 'simple' for one user "
            "is complex for another. They also inflate sentence length without adding information. "
            "Technical writing must describe actions, not evaluate their difficulty."
        ),
        "detection_pattern": ["simply", "easily", "quickly", "basically", "very", "just"],
        "bad_examples": [
            "Simply click Save to finish.",
            "You can easily configure this setting.",
            "The system quickly processes the request."
        ],
        "good_examples": [
            "Click Save to finish.",
            "Configure this setting in the Properties panel.",
            "The system processes the request in under two seconds."
        ],
        "fix_instruction": (
            "Delete the adverb. If it was conveying speed or effort, replace it with a "
            "measurable fact (e.g., 'in under two seconds', 'in three steps') or remove "
            "the qualifier entirely."
        ),
    },

    {
        "id": "VAGUE_001",
        "category": "Clarity & Precision",
        "severity": "error",
        "rule": "Ambiguous nouns (stuff, things, something, etc.) must be replaced with specific terms.",
        "why": (
            "Vague nouns fail to communicate precise meaning and cause translation errors. "
            "They indicate the writer has not fully identified the subject and require "
            "the reader to guess — an unacceptable burden in industrial documentation."
        ),
        "detection_pattern": ["stuff", "things", "something", "anything", "everything", "item", "aspect"],
        "bad_examples": [
            "Make sure all the things are configured correctly.",
            "Enter something in the Name field.",
            "Check if anything is missing."
        ],
        "good_examples": [
            "Ensure all parameters are configured correctly.",
            "Enter a unique identifier in the Name field.",
            "Verify that all required fields contain values."
        ],
        "fix_instruction": (
            "Replace the vague noun with the precise technical term for the subject. "
            "Consult the product glossary or UI labels for the correct terminology."
        ),
    },

    {
        "id": "ARTICLE_001",
        "category": "Clarity & Precision",
        "severity": "info",
        "rule": "Remove unnecessary articles before positional references ('the following', 'the below').",
        "why": (
            "'The following' and 'the below' are set phrases that function as adjectives. "
            "Adding 'the' before them is redundant. Additionally, 'below' as a positional "
            "reference is fragile in single-sourced or reordered content."
        ),
        "detection_pattern": ["the following", "the below", "the above"],
        "bad_examples": [
            "Refer to the following table for details.",
            "See the below steps.",
            "As shown in the above figure."
        ],
        "good_examples": [
            "Refer to the following table.",
            "Complete the following steps.",
            "As shown in Figure 3."
        ],
        "fix_instruction": (
            "Remove 'the' when it precedes 'following'. Replace 'the below' with 'the following'. "
            "Replace 'the above' with a specific cross-reference (e.g., 'Figure 3', 'Table 2')."
        ),
    },

    {
        "id": "JARGON_001",
        "category": "Clarity & Precision",
        "severity": "warning",
        "rule": "Corporate jargon (utilize, leverage, facilitate, optimize) must be replaced with plain verbs.",
        "why": (
            "Corporate jargon inflates register without adding precision. 'Utilize' means 'use'; "
            "'leverage' means 'use'; 'facilitate' means 'help' or 'enable'. These words create "
            "translation difficulty and exclude non-native English readers."
        ),
        "detection_pattern": ["utilize", "leverage", "facilitate", "optimize", "synergize", "streamline"],
        "bad_examples": [
            "Utilize the API to retrieve data.",
            "Leverage the built-in scheduler.",
            "This feature facilitates data transfer."
        ],
        "good_examples": [
            "Use the API to retrieve data.",
            "Use the built-in scheduler.",
            "This feature transfers data."
        ],
        "fix_instruction": (
            "Replace: utilize → use, leverage → use, facilitate → enable/allow/help, "
            "optimize → improve/tune, streamline → simplify. "
            "Choose the plainest verb that preserves the original meaning."
        ),
    },

    # ─────────────────────────────────────────
    # 6. GRAMMAR & FORMALITY
    # ─────────────────────────────────────────
    {
        "id": "OXFORD_001",
        "category": "Grammar & Formality",
        "severity": "warning",
        "rule": "Oxford Comma is required in all series of three or more items.",
        "why": (
            "The Oxford (serial) comma eliminates ambiguity in lists. Without it, "
            "the last two items can be read as a paired unit rather than separate items. "
            "In technical documentation, this can cause dangerous misinterpretation of "
            "enumerated requirements or steps."
        ),
        "detection_pattern": ["X, Y and Z", "X, Y or Z"],
        "bad_examples": [
            "Configure the hostname, port and timeout.",
            "Select Read, Write or Execute permissions."
        ],
        "good_examples": [
            "Configure the hostname, port, and timeout.",
            "Select Read, Write, or Execute permissions."
        ],
        "fix_instruction": (
            "Insert a comma before the final conjunction ('and' or 'or') in every series "
            "of three or more items."
        ),
    },

    {
        "id": "CONTRACTION_001",
        "category": "Grammar & Formality",
        "severity": "error",
        "rule": "Contractions are prohibited in formal technical documentation.",
        "why": (
            "Contractions are informal register markers inappropriate for industrial, "
            "regulatory, or enterprise documentation. They also cause issues in translation "
            "memory tools, as contracted and expanded forms may be stored as separate strings."
        ),
        "detection_pattern": [
            "don't", "can't", "isn't", "won't", "doesn't", "it's",
            "you're", "they're", "we're", "haven't", "didn't", "wouldn't"
        ],
        "bad_examples": [
            "Don't click Cancel before saving.",
            "The system can't process the request.",
            "It's important to back up your data."
        ],
        "good_examples": [
            "Do not click Cancel before saving.",
            "The system cannot process the request.",
            "Back up data before proceeding."
        ],
        "fix_instruction": (
            "Expand all contractions to their full forms: "
            "don't → do not, can't → cannot, isn't → is not, "
            "won't → will not, it's → it is (or restructure to remove entirely)."
        ),
    },

    {
        "id": "GENDER_001",
        "category": "Grammar & Formality",
        "severity": "warning",
        "rule": "Gender-specific language must be replaced with inclusive alternatives.",
        "why": (
            "Gender-specific pronouns and nouns (he, she, his, her, mankind, manpower) "
            "exclude a portion of the audience and fail inclusive writing standards "
            "required by most enterprise style guides and localization guidelines."
        ),
        "detection_pattern": ["\\bhe\\b", "\\bshe\\b", "\\bhis\\b", "\\bher\\b", "mankind", "manpower"],
        "bad_examples": [
            "The administrator must update his password.",
            "She can configure the device remotely.",
            "Mankind has benefited from automation."
        ],
        "good_examples": [
            "The administrator must update their password.",
            "Administrators can configure the device remotely.",
            "Users benefit from automation."
        ],
        "fix_instruction": (
            "Replace gendered pronouns with 'they/their' (singular they is grammatically "
            "accepted in modern style guides including Chicago and APA). "
            "Alternatively, rewrite using the role noun as subject to avoid pronouns entirely."
        ),
    },

    # ─────────────────────────────────────────
    # 7. PROCEDURAL LOGIC
    # ─────────────────────────────────────────
    {
        "id": "ACTION_001",
        "category": "Procedural Logic",
        "severity": "error",
        "rule": "A single procedural step must contain only one action.",
        "why": (
            "Compound steps (joined by 'then', 'next', 'after that') create cognitive load "
            "and make it impossible to track completion of individual actions. "
            "They also break automated step-counting and localization tooling."
        ),
        "detection_pattern": ["then", "after that", "next,", "and then"],
        "bad_examples": [
            "Click Save and then restart the service.",
            "Enter your credentials, then click Login.",
            "Open the file, after that click Edit."
        ],
        "good_examples": [
            "1. Click Save.\n2. Restart the service.",
            "1. Enter your credentials.\n2. Click Login.",
            "1. Open the file.\n2. Click Edit."
        ],
        "fix_instruction": (
            "Split the sentence at the conjunction ('then', 'and then', 'after that') into "
            "two separate numbered steps. Each step starts with its own action verb."
        ),
    },

    {
        "id": "LIST_001",
        "category": "Procedural Logic",
        "severity": "error",
        "rule": "Action fusion in list items must be split into separate steps.",
        "why": (
            "When two distinct actions appear in one list item (e.g., 'Click Save and restart'), "
            "the reader cannot check off or track each action independently. "
            "Fused actions also prevent accurate step-level feedback in AI-assisted review."
        ),
        "detection_pattern": ["and restart", "and then click", "and close", "and verify", "and confirm"],
        "bad_examples": [
            "Click Save and restart the application.",
            "Select the file and click Open.",
            "Enter the value and confirm with Enter."
        ],
        "good_examples": [
            "1. Click Save.\n2. Restart the application.",
            "1. Select the file.\n2. Click Open.",
            "1. Enter the value.\n2. Press Enter."
        ],
        "fix_instruction": (
            "Identify the point where the second action begins (usually after 'and'). "
            "Split into two separate list items, each beginning with its own verb."
        ),
    },

    {
        "id": "LIST_002",
        "category": "Procedural Logic",
        "severity": "warning",
        "rule": "A heading must not end with a colon when immediately followed by numbered steps.",
        "why": (
            "A colon at the end of a heading before a numbered list creates a punctuation "
            "conflict — headings are self-contained; colons introduce run-on content. "
            "Most structured authoring tools and DITA standards prohibit this pattern."
        ),
        "detection_pattern": ["heading ending with :", "## Title:", "### Section:"],
        "bad_examples": [
            "## To install the application:\n1. Download the installer.",
            "### Configuration steps:\n1. Open the settings panel."
        ],
        "good_examples": [
            "## Install the Application\n1. Download the installer.",
            "### Configure the Application\n1. Open the settings panel."
        ],
        "fix_instruction": (
            "Remove the colon from the heading. Rewrite the heading as an imperative phrase "
            "or noun phrase (not a sentence fragment ending with a colon)."
        ),
    },

    {
        "id": "CONDITIONAL_001",
        "category": "Procedural Logic",
        "severity": "warning",
        "rule": "Complex if-then conditional structures must be flattened or restructured.",
        "why": (
            "Nested or multi-clause conditionals ('If A, and if B, then do C, otherwise do D') "
            "are cognitively demanding and difficult to translate. They should be converted "
            "into decision tables, branching steps, or separate procedures per condition."
        ),
        "detection_pattern": ["if.*then.*otherwise", "if.*and if", "depending on whether"],
        "bad_examples": [
            "If the device is online and the firmware is outdated, then update it, otherwise skip this step.",
            "If the connection fails, try restarting; if it still fails, contact support."
        ],
        "good_examples": [
            "**If the device is online:**\n1. Check the firmware version.\n2. Update if outdated.\n\n**If the device is offline:** Skip to Step 5.",
            "1. Restart the device.\n2. If the connection still fails, contact support."
        ],
        "fix_instruction": (
            "Identify each conditional branch. Create a separate step block or sub-procedure "
            "for each branch, labeled with the condition (e.g., 'If X:' as a step prefix). "
            "For two or more conditions, use a decision table."
        ),
    },

    # ─────────────────────────────────────────
    # 8. TABLES
    # ─────────────────────────────────────────
    {
        "id": "TABLE_001",
        "category": "Tables",
        "severity": "error",
        "rule": "Empty table cells are prohibited.",
        "why": (
            "Empty cells are ambiguous — they may mean 'not applicable', 'unknown', "
            "'same as above', or 'intentionally blank'. Translation engines and screen readers "
            "cannot interpret intent. Each cell must contain a value or an explicit placeholder."
        ),
        "detection_pattern": ["<td></td>", "| |", "empty cell"],
        "bad_examples": [
            "| Parameter | Default | Description |\n|-----------|---------|-------------|\n| Timeout   |         | Max wait    |"
        ],
        "good_examples": [
            "| Parameter | Default | Description |\n|-----------|---------|-------------|\n| Timeout   | 30 s    | Max wait    |",
            "Use 'N/A' for not applicable, '—' for intentionally empty, or a specific value."
        ],
        "fix_instruction": (
            "Fill every empty cell with: the actual value, 'N/A' (not applicable), "
            "'—' (intentionally blank, defined in table legend), or a descriptive placeholder. "
            "Never leave a cell empty without explicit notation."
        ),
    },

    {
        "id": "TABLE_002",
        "category": "Tables",
        "severity": "error",
        "rule": "Merged cells (colspan/rowspan) are prohibited in documentation tables.",
        "why": (
            "Merged cells break automated data extraction, translation memory alignment, "
            "DITA/XML publishing pipelines, and screen reader traversal. "
            "They also make table maintenance error-prone when rows or columns are reordered."
        ),
        "detection_pattern": ["colspan", "rowspan", "merged cell"],
        "bad_examples": [
            "<td colspan='2'>Shared Header</td>",
            "A cell spanning three rows to group related parameters."
        ],
        "good_examples": [
            "Repeat the header value in each cell instead of merging.",
            "Split the table into two separate tables if grouping is needed.",
            "Use a 'Group' column with a repeated label instead of a merged row header."
        ],
        "fix_instruction": (
            "Unmerge all cells. Repeat the value from the merged cell in each individual cell "
            "it previously covered. If grouping is essential, add a dedicated 'Category' or "
            "'Group' column and repeat the group label per row."
        ),
    },

    # ─────────────────────────────────────────
    # 9. TRANSLATION & CONSISTENCY
    # ─────────────────────────────────────────
    {
        "id": "PVERB_001",
        "category": "Translation & Consistency",
        "severity": "warning",
        "rule": "Phrasal verbs (set up, shut down, turn on) must be replaced with single-word equivalents.",
        "why": (
            "Phrasal verbs are idiomatic and localize poorly. Machine translation systems "
            "often render them literally, producing incorrect output. "
            "Single-word Latinate verbs (configure, terminate, enable) are universally understood "
            "and translate correctly across all major language pairs."
        ),
        "detection_pattern": [
            "set up", "shut down", "turn on", "turn off", "log in", "log out",
            "plug in", "pull up", "bring up", "kick off", "wrap up"
        ],
        "bad_examples": [
            "Set up the connection.",
            "Shut down the device.",
            "Turn on the feature.",
            "Log in to the portal."
        ],
        "good_examples": [
            "Configure the connection.",
            "Shut down → Power off / Terminate the device.",
            "Enable the feature.",
            "Sign in to the portal."
        ],
        "fix_instruction": (
            "Replace phrasal verbs with single-word alternatives: "
            "set up → configure/install, shut down → power off/terminate, "
            "turn on → enable/activate, turn off → disable/deactivate, "
            "log in → sign in, log out → sign out, plug in → connect."
        ),
    },

    {
        "id": "TRANS_001",
        "category": "Translation & Consistency",
        "severity": "error",
        "rule": "Idioms and figurative expressions must be replaced with literal language.",
        "why": (
            "Idiomatic expressions ('at the end of the day', 'in a nutshell', 'hit the ground running') "
            "are culture-specific and untranslatable literally. They produce incorrect or absurd "
            "translations and confuse non-native English readers. Technical documentation "
            "must use literal, denotative language exclusively."
        ),
        "detection_pattern": [
            "at the end of the day", "in a nutshell", "hit the ground running",
            "keep in mind", "bear in mind", "touch base", "ballpark", "low-hanging fruit"
        ],
        "bad_examples": [
            "At the end of the day, the system must be stable.",
            "In a nutshell, the API handles authentication.",
            "Keep in mind that the timeout value affects performance."
        ],
        "good_examples": [
            "The system must remain stable during operation.",
            "The API handles authentication.",
            "Note: The timeout value affects performance."
        ],
        "fix_instruction": (
            "Identify the literal meaning of the idiom and rewrite using that meaning directly. "
            "Remove the idiomatic phrase entirely and replace with a plain declarative statement."
        ),
    },

    {
        "id": "TRANS_002",
        "category": "Translation & Consistency",
        "severity": "warning",
        "rule": "Ambiguous quantity words (various, multiple, different, several) must be replaced with specific values.",
        "why": (
            "Vague quantifiers are untestable and unverifiable. 'Various settings' — how many? "
            "Which ones? In regulated industries (IEC, ISO, FDA), documentation must be "
            "precise enough to serve as a reference without additional interpretation."
        ),
        "detection_pattern": ["various", "multiple", "several", "different", "numerous", "many"],
        "bad_examples": [
            "Various configuration options are available.",
            "The system supports multiple protocols.",
            "Several parameters must be set before deployment."
        ],
        "good_examples": [
            "The following five configuration options are available: [list].",
            "The system supports Modbus TCP, IEC 60870-5-104, and OPC UA.",
            "Set the following three parameters before deployment: Hostname, Port, Timeout."
        ],
        "fix_instruction": (
            "Replace the vague quantifier with: (a) the exact count, (b) an explicit list, "
            "or (c) a cross-reference to a table that enumerates all items. "
            "If the count is genuinely variable, write 'one or more' instead of 'multiple'."
        ),
    },

    {
        "id": "CONSIST_001",
        "category": "Translation & Consistency",
        "severity": "error",
        "rule": "UI interaction verbs must be consistent throughout a single task or document.",
        "why": (
            "Mixing interaction verbs for the same UI element type (e.g., 'Click Save' in "
            "step 1 and 'Select Exit' in step 3 for the same type of action) creates "
            "translation memory fragmentation and confuses readers about whether a different "
            "gesture is required. One verb per interaction type per document."
        ),
        "detection_pattern": ["mixed: click/select", "mixed: press/click", "mixed: tap/select"],
        "bad_examples": [
            "Step 1: Click Save.\nStep 3: Select Cancel.",
            "Step 2: Press Enter.\nStep 4: Click Confirm."
        ],
        "good_examples": [
            "Step 1: Click Save.\nStep 3: Click Cancel.",
            "Step 2: Click Confirm.\nStep 4: Click OK."
        ],
        "fix_instruction": (
            "Audit all UI interaction verbs in the task. Select one verb per interaction type "
            "and apply it consistently: 'Click' for mouse button actions, 'Select' for "
            "choosing from a list/dropdown, 'Enter' for keyboard text input, 'Press' for "
            "physical keys. Replace inconsistent verbs to match the chosen standard."
        ),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# ChromaDB Loader
# ─────────────────────────────────────────────────────────────────────────────

def build_retrieval_text(rule: dict) -> str:
    """
    Concatenates all semantically rich fields into a single embedding string.
    This is what ChromaDB will vectorise for similarity search.
    """
    bad = " | ".join(rule["bad_examples"])
    good = " | ".join(rule["good_examples"])
    patterns = " | ".join(rule["detection_pattern"])
    return (
        f"Rule ID: {rule['id']}\n"
        f"Category: {rule['category']}\n"
        f"Rule: {rule['rule']}\n"
        f"Why it matters: {rule['why']}\n"
        f"Detection patterns: {patterns}\n"
        f"Bad examples: {bad}\n"
        f"Good examples: {good}\n"
        f"Fix instruction: {rule['fix_instruction']}"
    )


def ingest_into_chromadb(persist_path: str = "./docscanner_rules_db"):
    """
    Ingests all 27 remediation rules into a ChromaDB persistent collection.
    Run once to populate; re-run to update (upsert semantics).

    Usage:
        from rule_remediations import ingest_into_chromadb
        ingest_into_chromadb()
    """
    import chromadb
    from chromadb.utils import embedding_functions
    import os

    # Ensure directory exists
    os.makedirs(persist_path, exist_ok=True)

    client = chromadb.PersistentClient(path=persist_path)
    ef = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="rule_remediations",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [r["id"] for r in RULE_REMEDIATIONS]
    documents = [build_retrieval_text(r) for r in RULE_REMEDIATIONS]
    metadatas = [
        {
            "rule_id": r["id"],
            "category": r["category"],
            "severity": r["severity"],
            "fix_instruction": r["fix_instruction"],
            "bad_examples": " | ".join(r["bad_examples"]),
            "good_examples": " | ".join(r["good_examples"]),
        }
        for r in RULE_REMEDIATIONS
    ]

    # Upsert so re-runs don't duplicate
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Ingested {len(RULE_REMEDIATIONS)} rules into '{persist_path}/rule_remediations'")
    return collection


# ─────────────────────────────────────────────────────────────────────────────
# Retrieval Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_remediation_by_id(collection, rule_id: str) -> dict | None:
    """
    Exact lookup by rule ID — use this when the detector is confident.
    Returns the metadata dict or None if not found.
    """
    result = collection.get(ids=[rule_id], include=["documents", "metadatas"])
    if result["ids"]:
        return {
            "rule_id": rule_id,
            "document": result["documents"][0],
            "metadata": result["metadatas"][0],
        }
    return None


def get_remediation_semantic(collection, flagged_sentence: str, top_k: int = 3) -> list:
    """
    Semantic fallback — use when rule ID is uncertain or for fuzzy matching.
    Returns top_k closest rules with distance scores.
    """
    results = collection.query(
        query_texts=[flagged_sentence],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    if not results or not results["ids"]:
        return []
        
    extracted = []
    for i in range(len(results["ids"][0])):
        extracted.append({
            "rule_id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return extracted


if __name__ == "__main__":
    ingest_into_chromadb()
