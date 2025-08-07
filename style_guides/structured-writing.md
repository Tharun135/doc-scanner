---
tags:
    - Documentation
    - Template
---

# Documentation template

This documentation template provides contributors with the necessary components and a standardized format in one file for structured writing. Contents include:

- It introduces the idea of a template first,
- provides you with guidelines for documentation writing and
- presents highlight elements for a harmonized appearance of documentation throughout the manifold software documentations provided through mk-docs

## How to use this template

First of all; you don't have to worry about the whole template. We built this template by starting at the top with the essential parts that you should definitely take care of, and will come the optional parts that you can take care of.

Essential parts:

- Check, if all necessary sections are included. (Done by developers)
- Check markdownlint issues (Done by developers)
- Check the documentation if the corresponding personas, like "Edge User" (OT Otto, Erdem Edge Operator) and "Andy App developer" or "David Device Builder" are addressed (Done by developers together with Technical writer)

Optional parts:

- Check the documentation, if it is written from customers point of view (Workflow and context information) (Done by Technical Writer)
- Check that the number of screenshots is appropriate to guide users, e.g. if there is a huge amount of text only, or if the content is very complex, etc. (Technical Writer); Use necessary and suitable screenshots only.
- Check that the titles are written in a use case based style.

## Sections to be filled out

- Purpose of this document (What is this piece of documentation about? Who is it for? What does the user know after reading through this?)
- Prerequisites (What are the prerequisites of the user to successfully perform the steps?)
- Procedure: Step-by-Step or Description (What does the user have to do to get the result?)
- Result (What is the status after the successful implementation?)

## Starting point (introduction = header)

This section describes the starting point of the user, where a contributor to content or a technical writer aims to create a new or updated version of documentation. Documentation will include some general descriptions of software installation, deployment, configuration and the like. To write your texts, you will set up a new mk document in English language and use several elements to structure your text, namely:

- Text
- Bullet points
- Pictures / Screenshots and pictures with highlights
- Videos
- Code snippets
- Notes
- Boxes
- Tables
- Copying code snippets (copy icon)
- Program code

## Elements of documentation pages

All the above mentioned elements to make documentation vivid and easy to read will be depicted in detail below.

### Text blocks

Text passaged should be precise, short and structured into paragraphs. The optimal length of a sentence is approx. 20 words. Please use pictures, bullet lists, tables etc. to make information easily accessible and readable already at a glance. Paragraphs will always have two or more sentences.
For highlighting specific words, bold font is advised. Use “Quotes” to indicate that you are talking about a specific command or section.
Icons can be integrated. All available icons can be found here: [link] .
Links can be used in-text or in a new line, to stand out. Links always need to be presented as a description of the target rather than the link itself.

### Bulleted lists

In documentation, it is good practice to avoid long narrations as in long text passages. Bulleted lists are easier to read and should be formatted in a lean way. It is advised to use a colon before starting the list or in the list, as the picture below illustrates. Good lists show the following characteristics:

- Start with a capital letter in each bullet section
- Keep a similar style of sentence structure in each section
- Show a minimum two bulleted sections
- End openly, i.e. they do not end with a full stop

### Numbered lists

Use numbered lists to structure action instructions in a sequence.

1. Start each action item with capital letter and write as sentence.
2. Start with the verb and avoid "you".
3. Don't use temporal words like "after that", "then", "at the end", which are redundant to the numbered list.
4. If there are interim results, add an intended line.

    Describe the state after the action in the indented line.

### Quote "Markdown code"

    ```
    - Start with a capital letter in each bullet section
    - Keep a similar style of sentence structure in each section
    - Show a minimum two bulleted sections
    - End openly, i.e. they do not end with a pull stop
    ```

### Pictures and screenshots

Use pictures to explain complex content. Use screenshots to emphasize steps in navigation. Pictures and screenshots should be stored as .PNG or .JPEG file in an "images" folder, on the same level as your markdown-file.
Solution of screenshots: 120 dpi.
Note: To ensure quality, don't change the solution of the screenshot afterwards.

![Folder structure for Images](assets/images/image_folder_structure.png)

The file can be displayed with the following code snippet:

??? example "Markdown code"

    ```markdown
    ![Name of the Image](path_to/the_image.png)
    ```

![Alt text](assets/images/Example_highlighted_picture.jpg)

!!! info "Highlighting pictures"
    For highlighting element in pictures, please use plain boxes in color orange (R 255, G 144 B 0 / #FF9000) in outline weight 1,5pt with rounded edges. For numbering of highlighted sections, please use position numbers a black and white oval, no filling, size 8pt.

### Videos

<iframe
width="560"
height="315"
src="https://www.youtube-nocookie.com/embed/uN40H9_IgUg"
title="YouTube video player"
frameborder="0"
allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen>
</iframe>

Embed videos to the page is simple and fast:

1. Search for the video on e.g. Youtube  
1. Click on the "Share" button and choose "Embed".  
![How to embed a video 1](assets/images/video_embed_1.png)
1. Copy the iframe and paste it to your Markdown page.  
![How-to-embed-a-video-2](assets/images/video_embed_2.png)
1. Done

??? example "Markdown code"

    ```markdown
    <iframe
    width="560"
    height="315"
    src="https://www.youtube-nocookie.com/embed/uN40H9_IgUg"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen>
    </iframe>
    ```

### Code snippets

To display short code snippet, that are just one command, or to reference a program, you can set a ` before and after the command.  

For example:  
Add the theme package to your project's dependencies and install it via your favorite Python package manager (`pip`, `poetry` etc).

??? example "Markdown code"

    ```markdown
    Add the theme package to your project's dependencies and install it via your favorite Python package manager (`pip`, `poetry` etc).
    ```

To write longer or more detailed snippets of code, it is often better to place them inside a code block. Code blocks allow you to use multiple lines, and markdown will render it inside its own box and with code type font.

To achieve this, start your block with a line of three backticks "\`\`\`". This signals to markdown that you are creating a code block.
You will need to finish with another line of three backticks.
If you have more than one version of a code snippet, you can sort them into a tab, which is defined by "=== 'Title'".

For example:

=== "3.x"

    ```yaml title="mkdocs.yml"
    markdown_extensions:
        - pymdownx.superfences:
            custom_fences:
                - name: mermaid
                  class: mermaid
                  format: !!python/name:pymdownx.superfences.fence_div_format

    extra_javascript:
        - https://cdn.siemens-web.com/js/mermaid/8.12.0/mermaid.min.js
    ```

=== "4.x"

    ```yaml title="mkdocs.yml"
    markdown_extensions:
        - pymdownx.superfences:
            custom_fences:
                - name: mermaid
                  class: mermaid
                  format: !!python/name:pymdownx.superfences.fence_code_format
    ```

??? example "Markdown code"

    ````

    === "3.x"

        ```yaml title="mkdocs.yml"
        markdown_extensions:
            - pymdownx.superfences:
                custom_fences:
                    - name: mermaid
                      class: mermaid
                      format: !!python/name:pymdownx.superfences.fence_div_format
    
        extra_javascript:
            - https://cdn.siemens-web.com/js/mermaid/8.12.0/mermaid.min.js
        ```
    
    === "4.x"
    
        ```yaml title="mkdocs.yml"
        markdown_extensions:
            - pymdownx.superfences:
                custom_fences:
                - name: mermaid
                    class: mermaid
                    format: !!python/name:pymdownx.superfences.fence_code_format
        ```
    ````

You can configure code snippet display features in your ``mkdocs.yml`` file.

To enable the copy button, insert the following into the "features" section:

```yml
theme:
  features:
    - content.code.copy
```

This will display the code snippet as:  

![copy snippet](assets/images/copy_snippet.png)

### Notices/Admonitions

Use notices/admonitions **only** for important notices, information, admonitions, etc. More information about the admonition types, their syntax and how to add admonitions for the Siemens warning system is available [here](../Markdown/Admonitions.md).

More information about when to use notices/admonitions is available [here](./RulesForContributors.md#using-notices-hintswarnings).

Admonitions are checked by [ft-syntax-linter.py](../../check/quality-measurements/fluid-topics-linter.md).

### Tables

To add a table, use three or more hyphens (---) to create each column's header, and use pipes (|) to separate each column. For compatibility, you should also add a pipe on either end of the row.

Example:  

| Title | Description |
| --- | --- |
| Example 1 | Info 1 |
| Example 2 | Info 2 |

??? example "Markdown code"

    ```markdown
    | Title | Description |
    | --- | --- |
    | Example 1 | Info 1 |
    | Example 2 | Info 2 |
    ```

### Quality check and finalization of documentation

Language check
Metadata

### Test Case

If one item of the following table does not suite your test discretion, you can remove the row from your test description.

| Test Title | Your test title |
| --- | --- |
| **Test Category** | Category |
| **Test No.** |  Test No. |
| **Description** | Your test description |
| **Preconditions** | Condition 1<br> Condition 2<br> Condition 3 |
| **Exception condition** | Exception rules for this test |
| **Warning condition** | Condition for which the test is not failed, yet the warning condition checks |
| **Failed condition** | Condition for which the test is failed |

??? Example "Procedure"
    | Steps | Action | Expected Result |
    | --- | --- | --- |
    | 1. | First step you need to do | Result that you expect |
    | 2. | Second step you need to do | Result that you expect |
    | 3. | Third step you need to do | Result that you expect |

??? example "Markdown code"
    ```
    | Test Title | Your test title |
    | --- | --- |
    | **Test Category** | Category |
    | **Test No.** |  Test No. |
    | **Description** | Your test description |
    | **Preconditions** | Condition 1<br> Condition 2<br> Condition 3 |
    | **Exception condition** | Exception rules for this test |
    | **Warning condition** | Condition for which the test is not failed, yet the warning condition checks |
    | **Failed condition** | Condition for which the test is failed |

    ??? Example "Procedure"
        | Steps | Action | Expected Result |
        | --- | --- | --- |
        | 1. | First step you need to do | Result that you expect |
        | 2. | Second step you need to do | Result that you expect |
        | 3. | Third step you need to do | Result that you expect |
    ```
