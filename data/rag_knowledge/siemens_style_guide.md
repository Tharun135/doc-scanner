# Siemens Style Guide for Contributors

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
- Avoid abbreviations - If abbreviations are needed, please define them first and make sure they are added to the global glossary.

### Specifying user interactions
- Use `++<key>++` to add keyboard shortcuts.
- If a topic describes a UI element that the user should click on or interact with, specify this with double quotation marks (Click on "OK").
- Entries in UI text fields should be added as inline code (Enter `1`).
- All terminal commands, code settings/parameters, messages, filenames etc. should be written in inline code or code blocks accordingly.

### Tone and voice
- Use natural, conversational language and not robotic, funny, cool, or clever.
- Address users in second-person (you) and use first-person plural for the application (we).
- Use gender-neutral language.
- Use polite language.
- Use 'please' and 'sorry' only when necessary.
- Use positive instead of negative framing.
- Use positive contractions to avoid sounding too formal.
- Avoid using negative contractions as they can appear too informal.

### Use of big and small letters (capitalization/casing)
- Capitalize the first letter of the first word in a title / sentence / tooltip / menu item / list item / button.
- Capitalize proper nouns, i.e. places, organizations, tools, languages, products and things: Siemens, SIMATIC PCS myexpert, iOS, JavaScript, MindSphere.
- Capitalize named app functions and UI elements: Go to Settings, Allocate users in User Management, Press OK.

### Headings
- If the text under a heading is a description of what the user should do, use an active sentence and not an imperative one.
- Use short descriptive headings before explanations/tables etc.

### Grammar tenses
- Use present simple tense to describe an action or instruction.
- Only use simple verb forms in the past or future when necessary.
- **Good:** click, browse, upload.
- **Bad:** clicking, being clicked, was clicking.

### Active voice
- **Good:** Click submit.
- **Bad:** Submit is clicked by the user.

### Time-based vocabulary: Last, latest and recent
- **Last** implies nothing else will follow. It's the last, and after this it is finished.
- **Latest** implies that it is the last to date, which means there could be more to follow. Most recent. Newest.
- **Recent** is more time focused and is similar to latest. It means that it happened a short time ago.

## Words/Phrases to avoid

| Word/Phrase | Explanation |
| --- | --- |
| For that reason | filler expression |
| Therefore | filler word |
| According | filler word |
| Furthermore | filler word |
| to do | too generic |
| should | provides room for interpretation |
| could | provides room for interpretation |
| master/slave | Not appropriate due to miss-interpretation |
| It is / there is / there are | weak expressions |
| Nominalized verbs | They are coupled with weaker verbs. |
| please | Not necessary |
| simply / it's very easy / just | Too colloquial. |
| e.g. | Avoid abbreviations |

## Structural Rules & Markdown Linting

- **Tables:** Ensure all table separator rows use format `| --- | --- |` with spaces around pipes.
- **Emphasis Formatting:** Remove spaces inside emphasis markers (e.g., `_text_` not `_text _`).
- **Heading Formatting:** Add space after hash in headings: `# Heading`. No punctuation at the end of headings.
- **Lists:** Fix markdown list indentation. Lines that appear after blank lines within numbered or bulleted list items must be indented with 4 spaces to properly associate them as subitems. Add a space after list markers: `- Item`.
- **Procedural Steps:** In procedural steps, when you continue a step's content on the next line, add two trailing spaces at the end of the previous line. Each step must describe a single, discrete user action.
- **No abbreviations like e.g.**
- **Use the "-ing"-form of verbs in headlines.**
- **Small letters in headlines except the first one and for proper names.**

*End of Style Guide Base Knowledge*
