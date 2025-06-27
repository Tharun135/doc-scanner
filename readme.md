# Doc-Scanner

**A sophisticated style guide checker that leverages AI to provide intelligent feedback and suggestions for document improvements. This tool analyzes documents for style guide compliance and generates actionable AI-powered recommendations.**

## 🎯 Key Features

* **Automated style guide compliance checking** - Real-time validation against customizable style rules
* **AI-powered feedback generation** - Intelligent suggestions for improving document quality
* **Real-time document analysis** - Instant feedback as you type or upload content
* **Customizable style rules** - Modular rule-based system for easy addition of new guidelines
* **Detailed suggestion reports** - Comprehensive analysis with line-by-line recommendations
* **Terminology validation** - Ensures consistent usage of specific terms and suggests corrections
* **Stylistic guidelines enforcement** - Grammar, punctuation, and formatting rule compliance
* **Inclusivity checks** - Identifies non-inclusive language and suggests alternatives
* **User-friendly web interface** - Simple, intuitive interface for easy content analysis

## 🛠️ Technologies

* **Python** - Core application framework
* **Flask** - Web application framework
* **Natural Language Processing** - Advanced text analysis capabilities
* **spaCy** - Industrial-strength NLP library
* **AI/ML for text analysis** - Intelligent pattern recognition and suggestion generation

## 🔍 Use Cases

* **Technical documentation review** - Ensure consistency across technical content
* **Content style consistency checks** - Maintain uniform voice and style
* **Writing quality improvement** - Enhance clarity and professionalism
* **Style guide enforcement** - Automated compliance with organizational standards
* **Document standardization** - Consistent formatting and terminology usage

## 📋 Table of Contents

* [Installation](#-getting-started)
* [Usage](#-usage)
* [Examples](#-examples)
* [Project Structure](#-project-structure)
* [Contributing](#-contributing)
* [License](#-license)
* [Contact](#-contact)

## 🚀 Getting Started

### Prerequisites

* Python 3.6 or higher
* Git (optional, for cloning the repository)

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Tharun135/doc-scanner.git
   cd doc-scanner
   ```

   Alternatively, download the repository as a ZIP file and extract it.

2. **Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   On macOS and Linux:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## 📖 Usage

### Running the Application

Start the Flask web server by running:

```bash
python app.py
```

The application will start on <http://localhost:5000>.

### Analyzing Content

1. Open your web browser and navigate to <http://localhost:5000>.
2. Paste or type your text content into the input field provided.
3. Click the Analyze button.
4. Review the suggestions displayed below the input field.

## 📋 Examples

### Sample Input

```text
Please backup your files regularly to prevent data loss.

Ensure Bluetooth is enabled on your device.

He requested access to the administrator panel.

Avoid using and/or in official documents.

Afterwards, we can review the results.
```

### Expected Suggestions

* Line 1: Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.
* Line 2: Capitalize 'Bluetooth' as it's a proper noun.
* Line 3: Use 'administrator' instead of 'admin' in content.
* Line 4: Avoid using 'and/or'; consider rephrasing for clarity.
* Line 5: Use 'afterward' instead of 'afterwards'.

## 🏗️ Project Structure

```text
doc-scanner/
├── app.py
├── requirements.txt
├── README.md
├── run.py
├── utils.py
├── test_transformers.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   └── index.html
├── app/
│   ├── __init__.py
│   ├── mstp_rules.py
│   ├── utils.py
│   ├── analysis_advanced.py
│   └── rules/
│       ├── __init__.py
│       ├── accessibility_terms.py
│       ├── ai_bot_terms.py
│       ├── grammar_word_choice.py
│       ├── passive_voice.py
│       ├── security_terms.py
│       ├── style_formatting.py
│       ├── technical_terms.py
│       └── ... (other rule files)
└── venv/
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! To contribute:

1. **Fork the Repository**
   Click the Fork button on the repository's GitHub page.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/doc-scanner.git
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/new-rule
   ```

4. **Make Your Changes**

   * Add new rules or improve existing ones
   * Ensure that your code follows the project's style guidelines
   * Test your changes thoroughly

5. **Commit Your Changes**

   ```bash
   git commit -am "Add new rule for XYZ"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/new-rule
   ```

7. **Submit a Pull Request**
   Go to the original repository and create a pull request from your forked repository.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions or support, please open an issue in the repository or contact:

* Email: <tharun135@gmail.com>

---

> [!IMPORTANT]  
> This tool is intended to assist with writing content in compliance with style guides. It provides intelligent suggestions to improve document quality and consistency. Always refer to your organization's official style guide for authoritative guidelines.
