---
tags:
    - Contributions
    - Basics
---

# Style guide for contributors

This topic provides a guide to support you in creating documentation content. It provides basic rules to help you write concisely, accurately and effectively. It also means that all created content is high quality and has a similar look and feel.

These guidelines are based on the [Siemens IX Design Guide](https://ix.siemens.io/docs/language/writing-style-guide-getting-started/){ .external-link } with adjustments made to focus on generating websites with Markdown/MkDocs.

## Naming conventions for files

When creating new files, follow these conventions:

- Do not use whitespace in the filename.
- Write the filename lower-case.
- Use `-` or `_` instead of whitespace.
- Use a use-case based filename that lines up with the file title.
    - Keep the filename as short as possible by leaving out pronouns and sticking to the key information.
    - Leave out product names if the file is in the product's subfolder.

    **Examples**

    | File title | Filename | Explanation |
    |---|---|---|
    | Deleting configurations of the App XY | ``deleting-configurations.md`` | The file is in ``app-xy`` subfolder. |
    | Creating your workspace | ``creating-workspace.md`` | Unneeded pronoun has been removed from the filename. |
    | Restoring files after deletion | ``restoring-files.md`` | "After deletion" is not needed in the context. |
    | Previewing changes in the browser<br>Previewing changes in VS Code | ``previewing-changes-browser.md``<br>``previewing-changes-vscode.md`` | Because there are different methods to preview, the method is also added to the filename. |

| Good | Bad |
|---|---|
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
- Avoid abbreviations - If abbreviations are needed, please define them first and make sure they are added to the [global glossary](../Markdown/Tooltips.md#using-abbreviations-in-all-files) if they are used regularly.

| Good | Bad |
|---|---|
| ``## Importing the app`` | ``## The process for importing an app`` |
| <ol><li>To import the app, proceed as follows:</li><li>To save the app, proceed as follows:</li><li>To delete the app, proceed as follows:</li></ol> | <ol><li>Import the app by following the steps below:</li><li>To save the app, perform the following steps:</li><li>You can delete the app by doing the following:</li></ol> |
| When importing an app from an external source, ensure all dependencies are correctly configured. Check that the app is compatible with the existing system architecture. This helps avoid potential integration issues. | When importing an app from an external source, it is crucial to ensure that all dependencies are correctly configured and that the app is compatible with the existing system architecture to avoid potential integration issues. |

### Specifying user interactions

- Use ``++<key>++`` to add [keyboard shortcuts](../Markdown/ExtendedContent.md#keys).
- If a topic describes a UI element that the user should click on or interact with, specify this with double quotation marks.
- Entries in UI text fields should be added as inline code.
- All terminal commands, code settings/parameters, messages, filenames etc. should be written in inline code or code blocks accordingly.

| Good | Bad |
|---|---|
| Click on "OK" | Click on ``OK`` |
| Enter ``1`` in the "Value" field. | Enter "1" in the ``Value`` field. |
| Change the value of the ``dataType`` setting to ``Boolean``. | Change the dataType to Boolean. |
| Add ``myfile.yml`` to the ``System`` folder. | Add "myfile.yml" to the "system" folder. |
| Enter the command and press ``++enter++`` | Enter the command and press "Enter" / [Enter] |

### Tone and voice

- Use natural, conversational language and not robotic, funny, cool, or clever
- Address users in second-person (you) and use first-person plural for the application (we)
- Use gender-neutral language
- Use polite language
- Use 'please' and 'sorry' only when necessary, for something inconvenient or unplanned
- Use positive instead of negative framing
- Use positive contractions to avoid sounding too formal
- Avoid using negative contractions as they can appear too informal

| Good                                  | Bad                           |
|---------------------------------------|-------------------------------|
| their, them, theirs, salesperson       | his, hers, him, salesman       |
| cannot, will not                       | can't, won't                   |
| appears when detail view has selected events | doesn't appear if detail view has no selected events |
| you will, we have                          | you'll, we've              |
| Welcome to this application            | Hey there!                     |
| such as, for example, including        | e. g., e.g.                    |

### Use of big and small letters (capitalization/casing)

- Capitalize the first letter of the first word in a title / sentence / tooltip / menu item / list item / button
- Capitalize proper nouns, i.e. places, organizations, tools, languages, products and things: Siemens, SIMATIC PCS myexpert, iOS, JavaScript, MindSphere
- Capitalize named app functions and UI elements: Go to Settings, Allocate users in User Management, Press OK

| Good                        | Bad                           |
| ----------------------------| -----------------------------|
| Go to Settings              | Go To Settings                |
| Press OK                    | Press Ok                      |
| Log in                       | LOG IN                        |
| For more information, see Siemens Industry Online Support. | For more information, see Siemens industry online support. |

### Headings

- If the text under a heading is a description of what the user should do, use an active sentence and not an imperative one.
    - Using a descriptive heading is usually better for the main heading (h1)
- Use short descriptive headings before explanations/tables etc.
- Only levels 2 and 3 are added to the table of contents on the right, so try to use level 4+ as little as possible.
    - In some cases, it may make sense to add a new topic/file.

| Good                        | Bad                                      |
| ----------------------------| -----------------------------------------|
| Adding a new element         | Add a new element                        |
| Configuration file structure | Description of the structure of the configuration file |

### Grammar tenses

- Use present simple tense to describe an action or instruction
- Only use simple verb forms in the past or future when necessary

| Good            | Bad                               |
| --------------- | ----------------------------------|
| click, browse, upload | clicking, being clicked, was clicking |
| file loads, file loaded | file is going to be loaded, file has been loaded |

### Active voice

| Good                    | Bad                                |
| ----------------------- | ----------------------------------|
| Configuration file opens | The configuration file is opened. |
| Click submit.            | Submit is clicked by the user.     |
| Admin provides read-only access. | Read-only access is provided by Admin. |
| Calculate the data.      | The data is calculated by the application. |
| Measure performance.     | Performance is measured.            |

### Minimalist punctuation

Always consider whether necessary.

- **``!``** Exclamation mark for high-level warnings only!
- **``?``** Question mark only if necessary
- **``:``** Use colons: especially to introduce lists
- **``.``** Full stops at the end of all full sentences
- **``.``** Full stops before all file extensions: .csv .txt .zip
- **``.``** Consistent use of full stops throughout the application
- **``…``** Ellipsis only for transitional text: Upload…
- **``'``** Single quotation mark for possession: Customer's role (single), customers' roles (plural)
- No quotation mark or brackets for plurals: PDFs
- **``&``** Avoid ampersands unless in a product or company name: Siemens & Halske AG
- **`*`** Avoid asterisks in applications
- **``(``** Avoid brackets ( ) and [ ]
- **``;``** Avoid semi-colons
- **``:``** Avoid and remove colons whenever possible, for example Username instead of Username:

Rule for commas: "If in doubt leave it out."

### Spacing​

- No space before %
- No space before colon, semi-colon, ellipsis
- Add a space after colon or semi-colon
- Add a space before and after quotation marks, hyphens, and em dashes
- Add a space before unit of measurement, e.g., 11 kg or 32 bits. Times are an exception, e.g., 11am or 4pm.

| Good      | Bad       |
|-----------|-----------|
| 50%       | 50 %      |
| 11am      | 11 am     |
| Browse…   | Browse …  |

### Lists​

- Consistent use of full stops in lists / bullet points
    - If lists / points are not full sentences, do not use full stops
    - Use fragments or full sentences in lists, not both
    - If a bullet / list item has two sentences, use full stops for this point and all others
- Make lists parallel, i.e. all items / bullets have the same look, length, feel, punctuation, capitalization
- Use lists for multiple examples, instead of a long list in the sentence
- Introduce lists, where possible, with a description of the list followed by a colon, e.g. "The following data types are available:"
- Use tables if the list items have descriptions/more information.
- Prioritize clarity when using multi-level ordered lists.
- Avoid excessive nesting. It makes it harder to follow the content.

**Good**

| Item | Description |
|---| ---|
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

Use screenshots for the following:

- To make the steps in a step-by-step guide clearer.
- To show the result of the action.
- Provide an overview of the app's layout.

When you use screenshots in the user documentation, make sure that you fulfill the following criteria:

- Light mode for app UI screenshots
- Red frame (3px border width, <span style="color:#FF0000; font-weight:700;">color #FF0000</span>) to highlight content in the UI
- Dark background (<span style="color:#000028; font-weight:700;">color #000028</span>) for overview graphics
- Blurred internal/private data
- Pay attention that the size of the screenshots is the same throughout a topic or chapter. For example, when creating screenshots from a wizard, take the screenshots one after the other so that the dialog size is the same.

    !!! hint "Adjust screenshot size with attribute lists"
        You can use [attribute lists](../Markdown/ExtendedContent.md#setting-the-width-of-an-image) to make the widths of screenshots in a step-by-step guide more consistent.

- Use the same settings, example project, etc. when creating screenshots that belong together.

### Using notices (hints/warnings)

- Make sure you use the correct syntax for notices.

    ```markdown
    !!! <hint type> "<hint title>"
        <hint text>
    ```

    - Make sure to add 4 spaces before the !!! if the hint is part of a list → The 2nd line then has 8 blank spaces
- Use the correct hint type where possible, e.g. "note" for something the user can copy, "info" for additional information, etc.
- Use the hint wherever necessary, instead of adding phrases like "please note" when writing content.
- Use hints only when needed. Some information can easily be added in an introductory sentence.
- If the information in the hint is required before the current action, make sure it is also written before the action.

!!! note "More information about hints"
    More information about hints is available [here](../Markdown/Admonitions.md)

### Time-based vocabulary: Last, latest and recent

- Last implies nothing else will follow. It's the last, and after this it is finished. No more are coming.
    - Use last for the version only if it really is the final version.
    - If you want to refer to the update/version before the current one, use "previous". Using "last" in this context is slang.
- Latest implies that it is the last to date, which means there could be more to follow. Most recent. Newest.
- Recent is more time focused and is similar to latest. It means that it happened a short time ago.

| Good      | Bad       |
|-----------|-----------|
| Latest update       | Last update      |
| Previous version      | Last version     |
| Recent events   | Last events  |

## Main writing principles

| Principle                                     | Explanation (if needed)                                              |
|-----------------------------------------------|----------------------------------------------------------------------|
| Same content belong together and is described at one location |  In this way, you can reduce links and context switches for the reader.                                                                     |
| Describe instructions based in chronological order. |                                                                      |
| State the condition before the activity        | Examples<ul><li>Before installing the app, run...</li><li>To run the command, open the terminal...</li><li>If you are not logged in, log in now.</li></ul>|
| Put the goal of an action at the beginning.      | So that the reader knows why they should follow the instructions. |
| Prevent conjunctive                            | Opens up too many possible interpretations. |
| No abbreviations like e.g.                     |                                                                      |
| Avoid explicit notes when possible.             | Too many explicit notes on a page interrupt the reading flow and distract from the important ones. Try first to add the information with a simple sentence. |
| Display complete code for examples.            | When integrating code examples in the documentation, please show the whole code, that users with low experience understand it at first sight.<br>Not:<br>"sld -t 192.168.0.1 i .\bin\1500 --accept-security-disclaimer"<br>But:<br>"**apax** sld -t 192.168.0.1 i .\bin\1500 --accept-security-disclaimer" |
| Use the "title" parameter for code blocks to describe which file is involved |Example:<br>"``json title="My json file"``<br>{<br>json code<br>}<br>...<br>The user then knows which file they are making changes to. |
| Avoid screenshots.                             | They risk being outdated very soon. |
| In places where the screenshots are a must, redact personal information, if any, before publishing them. | Review the screenshots for any sensitive or private information, such as names, addresses, phone numbers, or email addresses. Redact or blur such information on the screenshots and ensure privacy. |
| Limit the use of italic and bold text.         | Overwhelms the reader. |
| Use "-ing"-form of verbs in headlines.          | Better wording for a concrete description of workflows. |
| Small letters in headlines except the first one and for proper names. |Ensures a modern look. |
| Use active voice.                               | The reader can identify the actor more easily. |
| Write as use-case based as possible.            | What can the user do and how do they do it? |
| Use numbers to describe action steps.           | Break down what the user has to do into small steps in an ordered list.<br><ol><li>Open the program.</li><li>Open your project.</li><li>Right-click on the app and select "New file".</li></ol> |
| For product names, write the full name followed by its abbreviated form in parentheses. For example: SIMATIC Project SDC Control App (SDC DCA). | Avoids confusion.<br>After the initial introduction, continue to use the abbreviation throughout the document and create place holders. |
| Do not use returns in the middle of a sentence. | They are interpreted as a new sentence. This leads to ambiguity, especially during machine translation. |

## Words/Phrases to avoid

| Word/Phrase            | Explanation  |
|------------------------|--------------|
| For that reason         | filler expression |
| Therefore              | filler word |
| According              | filler word  |
| Furthermore            | filler word  |
| to do                  | too generic |
| should                 | provides room for interpretation |
| could                  | provides room for interpretation |
| master/slave           | [Not appropriate](https://en.wikipedia.org/wiki/Master/slave_(technology)){ .external-link }#Terminology_concerns) due to miss-interpretation (in 08/2020 there was a customer complain related to the US government at WESCO Distribution) |
| It is / there is / there are | weak expressions |
| Nominalized verbs      | They are coupled with weaker verbs. Example: "Each preparation of the solution is done twice." → "Each solution is prepared twice." |
| please                 | Not necessary |
| simply / it's very easy / just | Ok in the "Getting started" part of the documentation. For the rest of the documentation too colloquial. |
