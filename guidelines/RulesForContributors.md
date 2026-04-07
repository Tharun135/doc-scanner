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

**Examples**

| File title | Filename | Explanation |
| --- | --- | --- |
| Release notes for version 1.0.0 | `release-notes-v1_0_0.md` | The version delimiter is `_` because `.` would cause issues with services. |
| Deleting configurations of the App XY | `deleting-configurations.md` | The file is in the `app-xy` subfolder. |
| Creating your workspace | `creating-workspace.md` | Unneeded pronoun has been removed from the filename. |
| Restoring files after deletion | `restoring-files.md` | "After deletion" is not needed in the context. |
| Previewing changes in the browser / Previewing changes in VS Code | `previewing-changes-browser.md` / `previewing-changes-vscode.md` | Because there are different methods to preview, the method is also added to the filename. |

| Good | Bad |
| --- | --- |
| `developing-custom-app.md` / `developing_custom_app.md` | `developing a custom app.md` |
| `deleting-configurations.md` | `deletingConfigurations.md` / `DeletingConfigurations.md` |
| `configuring-app.md` | `configuration.md` |

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

| Good | Bad |
| --- | --- |
| `## Importing the app` | `## The process for importing an app` |
| 1. To import the app, proceed as follows. 2. To save the app, proceed as follows. | 1. Import the app by following the steps below. 2. To save the app, perform the following steps. |
| When importing an app from an external source, ensure all dependencies are correctly configured. Check that the app is compatible with the existing system architecture. This helps avoid potential integration issues. | When importing an app from an external source, it is crucial to ensure that all dependencies are correctly configured and that the app is compatible with the existing system architecture to avoid potential integration issues. |

### Specifying user interactions

- Use `++<key>++` to add keyboard shortcuts.
- If a topic describes a UI element that the user clicks on or interacts with, specify this with double quotation marks.
- Entries in UI text fields are added as inline code.
- All terminal commands, code settings/parameters, messages, filenames etc. are written in inline code or code blocks accordingly.

| Good | Bad |
| --- | --- |
| Click on "OK" | Click on `OK` |
| Enter `1` in the "Value" field. | Enter "1" in the `Value` field. |
| Change the value of the `dataType` setting to `Boolean`. | Change the dataType to Boolean. |
| Add `myfile.yml` to the "System" folder. | Add "myfile.yml" to the "system" folder. |
| Enter the command and press `++enter++` | Enter the command and press "Enter" / [Enter] |

### Tone and voice

- Use natural, conversational language and not robotic, funny, cool, or clever.
- Address users in second-person (you) and use first-person plural for the application (we).
- Use gender-neutral language.
- Use polite language.
- Use "please" and "sorry" only when necessary, for something inconvenient or unplanned.
- Use positive instead of negative framing.
- Use positive contractions to avoid sounding too formal.
- Avoid using negative contractions as they can appear too informal.

| Good | Bad |
| --- | --- |
| their, them, theirs, salesperson | his, hers, him, salesman |
| cannot, will not | can't, won't |
| appears when detail view has selected events | doesn't appear if detail view has no selected events |
| you will, we have | you'll, we've |
| Welcome to this application | Hey there! |
| such as, for example, including | e. g., e.g. |

### Use of big and small letters (capitalization/casing)

- Capitalize the first letter of the first word in a title, sentence, tooltip, menu item, list item, or button.
- Capitalize proper nouns, for example places, organizations, tools, languages, products and things: Siemens, SIMATIC PCS myexpert, iOS, JavaScript, MindSphere.
- Capitalize named app functions and UI elements: Go to Settings, Allocate users in User Management, Press OK.

| Good | Bad |
| --- | --- |
| Go to Settings | Go To Settings |
| Press OK | Press Ok |
| Log in | LOG IN |
| For more information, see Siemens Industry Online Support. | For more information, see Siemens industry online support. |

### Headings

- If the text under a heading describes what the user does, use an active sentence and not an imperative one.
    - A descriptive heading is usually better for the main heading (H1).
- Use short descriptive headings before explanations and tables.
- Only levels 2 and 3 are added to the table of contents on the right, so use level 4 and below as little as possible.
    - In some cases, it may make sense to add a new topic or file.

| Good | Bad |
| --- | --- |
| Adding a new element | Add a new element |
| Configuration file structure | Description of the structure of the configuration file |

### Grammar tenses

- Use present simple tense to describe an action or instruction.
- Only use simple verb forms in the past or future when necessary.

| Good | Bad |
| --- | --- |
| click, browse, upload | clicking, being clicked, was clicking |
| file loads, file loaded | file is going to be loaded, file has been loaded |

### Active voice

| Good | Bad |
| --- | --- |
| Configuration file opens. | The configuration file is opened. |
| Click submit. | Submit is clicked by the user. |
| Admin provides read-only access. | Read-only access is provided by Admin. |
| Calculate the data. | The data is calculated by the application. |
| Measure performance. | Performance is measured. |

### Minimalist punctuation

Always consider whether punctuation is necessary.

- `!` — Exclamation mark for high-level warnings only.
- `?` — Question mark only if necessary.
- `:` — Use colons to introduce lists.
- `.` — Full stops at the end of all full sentences.
- `.` — Full stops before all file extensions: `.csv` `.txt` `.zip`
- `…` — Ellipsis only for transitional text: Upload…
- `'` — Single quotation mark for possession: Customer's role (singular), customers' roles (plural).
- No quotation marks or brackets for plurals: PDFs.
- `&` — Avoid ampersands unless in a product or company name: Siemens & Halske AG.
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

| Good | Bad |
| --- | --- |
| 50% | 50 % |
| 11am | 11 am |
| Browse… | Browse … |

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

**Good**

| Item | Description |
| --- | --- |
| Element 1 | Description of element 1 |
| Element 2 | Description of element 2 |

**Bad**

- Element 1: Description of element 1
- Element 2: Description of element 2

**Good**

App 1 can work with the following apps:

- App 2
- App 4
- App 6
- App 7

**Bad**

App 1 can work with App 2, App 4, App 6 and App 7.

### Screenshots

Use screenshots to:

- Make the steps in a step-by-step guide clearer.
- Show the result of an action.
- Provide an overview of the app's layout.

When using screenshots in the user documentation, ensure the following criteria are met:

- Light mode for app UI screenshots.
- Red frame (3 px border width, color `#FF0000`) to highlight content in the UI.
- Dark background (color `#000028`) for overview graphics.
- Blurred internal or private data.
- Use the same screenshot size throughout a topic or chapter.
- Use the same settings, example project, etc. when creating screenshots that belong together.

### Using notices

Use the correct admonition syntax for all notices:

```markdown
!!! <type> "<TITLE>"
    Notice text.
```

Add 4 spaces before `!!!` if the notice is inside a list item. The notice text line then has 8 spaces.

The following notice types are available for the warning notice system:

| Type | Syntax | When to use |
| --- | --- | --- |
| Danger | `!!! danger "DANGER"` | Death or severe personal injury will result if proper precautions are not taken. |
| Warning | `!!! warning "WARNING"` | Death or severe personal injury may result if proper precautions are not taken. |
| Caution | `!!! tip "CAUTION"` | Minor personal injury can result if proper precautions are not taken. |
| Notice | `!!! info "NOTICE"` | Property damage can result if proper precautions are not taken. |

Additional notice types are available for informational content:

- Use `note` for information the user can copy or follow up on.
- Use `info` for additional context that does not fit the warning notice system.

**Examples**

!!! danger "DANGER"
    Indicates that death or severe personal injury will result if proper precautions are not taken.

!!! warning "WARNING"
    Indicates that death or severe personal injury may result if proper precautions are not taken.

!!! tip "CAUTION"
    Indicates that minor personal injury can result if proper precautions are not taken.

!!! info "NOTICE"
    Indicates that property damage can result if proper precautions are not taken.

Custom notice titles

Admonitions with a descriptive custom title — for example !!! info "Credentials for Databus" — represent named informational notices. Do not replace a custom title with "NOTICE".

The standard all-caps titles (DANGER, WARNING, CAUTION, NOTICE) are reserved for the warning notice system and indicate severity levels. A custom title signals that the admonition is contextually named and intentional.

Correct	Incorrect
!!! info "Credentials for Databus"	!!! info "NOTICE" (when a descriptive title is intended)
!!! info "NOTICE"	!!! info "Notice" (lowercase)
Rule: only replace an admonition title with "NOTICE" when the original title was not a deliberate descriptive label.

Additional guidelines for notices:

- Use notices wherever necessary instead of adding phrases like "please note" inline.
- Use notices only when needed. Some information fits better in an introductory sentence.
- If the notice content is required before an action, place it before that action.

### Time-based vocabulary: last, latest and recent

- **Last** implies nothing else follows. Use it only if it really is the final version. To refer to the version before the current one, use "previous."
- **Latest** implies it is the most recent to date, with more to follow.
- **Recent** is time-focused and means it happened a short time ago.

| Good | Bad |
| --- | --- |
| Latest update | Last update |
| Previous version | Last version |
| Recent events | Last events |

## Main writing principles

| Principle | Explanation |
| --- | --- |
| Same content belongs together and is described at one location. | This reduces links and context switches for the reader. |
| Describe instructions in chronological order. | |
| State the condition before the activity. | Examples: "Before installing the app, run..." / "To run the command, open the terminal..." / "If you are not logged in, log in now." |
| Put the goal of an action at the beginning. | The reader knows why they follow the instructions. |
| Avoid the conjunctive. | Opens up too many possible interpretations. |
| No abbreviations like "e.g." | |
| Avoid explicit notes when possible. | Too many notes on a page interrupt the reading flow. Try to add the information with a simple sentence first. |
| Display complete code for examples. | Users with low experience understand it at first sight. |
| Use the `title` parameter for code blocks to describe which file is involved. | Example: ` ```json title="myfile.json" ` — The reader knows which file they are making changes to. |
| Avoid screenshots. | They risk being outdated very soon. |
| Redact personal information in screenshots before publishing. | Review for names, addresses, phone numbers, or email addresses. Blur or redact before publishing. |
| Limit the use of italic and bold text. | Overwhelms the reader. |
| Use the `-ing` form of verbs in headings. | Provides a concrete description of workflows. |
| Use lowercase in headings except for the first word and proper names. | Ensures a modern look. |
| Use active voice. | The reader can identify the actor more easily. |
| Write as use-case based as possible. | What can the user do and how do they do it? |
| Use numbers to describe action steps. | Break down what the user has to do into small steps in an ordered list. |
| For product names, write the full name followed by the abbreviated form in parentheses, for example: SIMATIC Project SDC Control App (SDC DCA). After the initial introduction, continue with the abbreviation. | Avoids confusion. |
| Do not use line returns in the middle of a sentence. | They are interpreted as a new sentence. This leads to ambiguity, especially during machine translation. |

## Words and phrases to avoid

| Word or phrase | Explanation |
| --- | --- |
| For that reason | Filler expression |
| Therefore | Filler word |
| According | Filler word |
| Furthermore | Filler word |
| To do | Too generic |
| Should | Provides room for interpretation |
| Could | Provides room for interpretation |
| Master/slave | Not appropriate due to misinterpretation |
| It is / there is / there are | Weak expressions |
| Nominalized verbs | Coupled with weaker verbs. Example: "Each preparation of the solution is done twice." → "Each solution is prepared twice." |
| Please | Not necessary |
| Simply / it's very easy / just | Too colloquial outside of Getting started content |
