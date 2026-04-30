# Siemens Style Guide for Contributors - Context for LLM
SIEMENS_STYLE_GUIDE = """
# Style guide for contributors

This topic provides a guide to support you in creating documentation content. It provides basic rules to help you write concisely, accurately and effectively. It also means that all created content is high quality and has a similar look and feel.

These guidelines are based on the [Siemens IX Design Guide](https://ix.siemens.io/docs/language/writing-style-guide-getting-started/){ .external-link } with adjustments made to focus on generating websites with Markdown/MkDocs.

## Naming conventions for files

When creating new files, follow these conventions:

- Do not use whitespace in the filename.
- Do not use dot in the filename.
- Do not use special characters in the filename.
- Write the filename lower-case.
- Use `-` or `_` instead of dot or whitespace.
- Use a use-case based filename that lines up with the file title.
    - Keep the filename as short as possible by leaving out pronouns and sticking to the key information.
    - Leave out product names if the file is in the product's subfolder.

## Writing basics

### Style

- Use as few words as possible (less than 20 words per sentence).
- Break longer descriptions into smaller chunks.
- Write short headings.
- Use simple, specific, clear, and informative wording.
    - Do not avoid technical terms but consider if you need to explain them.
    - Define new or unfamiliar terms and use existing explanations (do not reinvent the wheel).
- Use the same words and grammatical forms, lengths, and styles repeatedly.
- Avoid abbreviations. If abbreviations are needed, define them first and make sure they are added to the global glossary if they are used regularly.

### Specifying user interactions

- Use ++<key>++ to add keyboard shortcuts.
- If a topic describes a UI element that the user clicks on or interacts with, specify this with double quotation marks.
- Entries in UI text fields are added as inline code.
- All terminal commands, code settings/parameters, messages, filenames etc. are written in inline code or code blocks accordingly.

### Tone and voice

- Use natural, conversational language and not robotic, funny, cool, or clever.
- Address users in second-person (you) and use first-person plural for the application (we).
- Use gender-neutral language.
- Use polite language.
- Use "please" and "sorry" only when necessary, for something inconvenient or unplanned.
- Use positive instead of negative framing.
- Use positive contractions to avoid sounding too formal.
- Avoid using negative contractions as they can appear too informal.

### Use of big and small letters (capitalization/casing)

- Capitalize the first letter of the first word in a title, sentence, tooltip, menu item, list item, or button.
- Capitalize proper nouns, for example places, organizations, tools, languages, products and things: Siemens, SIMATIC PCS myexpert, iOS, JavaScript, MindSphere.
- Capitalize named app functions and UI elements: Go to Settings, Allocate users in User Management, Press OK.

### Headings

- If the text under a heading describes what the user does, use an active sentence and not an imperative one.
    - A descriptive heading is usually better for the main heading (H1).
- Use short descriptive headings before explanations and tables.
- Only levels 2 and 3 are added to the table of contents on the right, so use level 4 and below as little as possible.
    - In some cases, it may make sense to add a new topic or file.

### Grammar tenses

- Use present simple tense to describe an action or instruction.
- Only use simple verb forms in the past or future when necessary.

### Active voice

- Configuration file opens.
- Click submit.
- Admin provides read-only access.
- Calculate the data.
- Measure performance.

### Minimalist punctuation

Always consider whether punctuation is necessary.

- ! — Exclamation mark for high-level warnings only.
- ? — Question mark only if necessary.
- : — Use colons to introduce lists.
- . — Full stops at the end of all full sentences.
- . — Full stops before all file extensions: .csv .txt .zip
- … — Ellipsis only for transitional text: Upload…
- ' — Single quotation mark for possession: Customer's role (singular), customers' roles (plural).
- No quotation marks or brackets for plurals: PDFs.
- & — Avoid ampersands unless in a product or company name: Siemens & Halske AG.
- Avoid asterisks.
- Avoid brackets.
- Avoid semi-colons.
- Avoid and remove colons wherever possible, for example: Username instead of Username:

Rule for commas: "If in doubt leave it out."

### Spacing

- No space before %.
- No space before colon, semi-colon, or ellipsis.
- Add a space after colon or semi-colon.
- Add a space before and after quotation marks, hyphens, and em dashes.
- Add a space before unit of measurement, for example 11 kg or 32 bits. Times are an exception, for example 11am or 4pm.

### Lists

- Use full stops consistently in lists and bullet points.
    - If list items are not full sentences, do not use full stops.
    - Use fragments or full sentences in lists, not both.
    - If a bullet item has two sentences, use full stops for that item and all others.
- Make lists parallel, for example all items have the same look, length, feel, punctuation, and capitalization.
- Use lists for multiple examples instead of a long inline list.
- Introduce lists with a description followed by a colon, for example: "The following data types are available:"
- Use tables if the list items have descriptions or more information.
- Prioritize clarity when using multi-level ordered lists.
- Avoid excessive nesting. It makes it harder to follow the content.

### Screenshots

Use screenshots to:
- Make the steps in a step-by-step guide clearer.
- Show the result of an action.
- Provide an overview of the app's layout.

When using screenshots in the user documentation, ensure the following criteria are met:
- Light mode for app UI screenshots.
- Red frame (3 px border width, color #FF0000) to highlight content in the UI.
- Dark background (color #000028) for overview graphics.
- Blurred internal or private data.
- Use the same screenshot size throughout a topic or chapter.
- Use the same settings, example project, etc. when creating screenshots that belong together.

### Using notices

Use the correct admonition syntax for all notices:

```markdown
!!! <type> "<TITLE>"
    Notice text.
```

The following notice types are available:
- Danger: !!! danger "DANGER"
- Warning: !!! warning "WARNING"
- Caution: !!! tip "CAUTION"
- Notice: !!! info "NOTICE"
- Note: use note for information the user can copy or follow up on.
- Info: use info for additional context.

### Time-based vocabulary: last, latest and recent

- Last implies nothing else follows. Use it only if it really is the final version. To refer to the version before the current one, use "previous."
- Latest implies it is the most recent to date, with more to follow.
- Recent is time-focused and means it happened a short time ago.

## Main writing principles

- Same content belongs together and is described at one location.
- Describe instructions in chronological order.
- State the condition before the activity.
- Put the goal of an action at the beginning.
- Avoid the conjunctive.
- No abbreviations like "e.g."
- Avoid explicit notes when possible.
- Display complete code for examples.
- Use the title parameter for code blocks to describe which file is involved.
- Avoid screenshots.
- Redact personal information in screenshots before publishing.
- Limit the use of italic and bold text.
- Use the -ing form of verbs in headings.
- Use lowercase in headings except for the first word and proper names.
- Use active voice.
- Write as use-case based as possible.
- Use numbers to describe action steps.
- For product names, write the full name followed by the abbreviated form in parentheses.
- Do not use line returns in the middle of a sentence.
- When a list item is followed by continuation content, end the list item line with two trailing spaces.

## Words and phrases to avoid

- For that reason (Filler expression)
- Therefore (Filler word)
- According (Filler word)
- Furthermore (Filler word)
- To do (Too generic)
- Should (Provides room for interpretation)
- Could (Provides room for interpretation)
- Master/slave (Not appropriate)
- It is / there is / there are (Weak expressions)
- Nominalized verbs
- Please (Not necessary)
- Simply / it's very easy / just (Too colloquial)
"""
