# ⚡ GitTLDR

> **AI-Powered Context-Aware Git Assistant for High-Velocity Developers**  
> *Built during the Build With Nova 48-Hour Hackathon (October 2026)*

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)
![CLI](https://img.shields.io/badge/Interface-Click%20%2B%20Rich-green.svg)
![Track](https://img.shields.io/badge/Track-AI%20for%20Developers-purple.svg)

---

## 📌 Problem Statement

Writing clear, semantic commit messages and comprehensive Pull Request templates takes mental energy and interrupts engineering flow. During fast sprints, developers frequently fall back to vague commit messages (`fix: minor changes`, `update stuff`) or skip PR summaries altogether. This creates technical debt, slows down peer reviews, and muddies git logs.

---

## 💡 The Solution

**GitTLDR** is a zero-friction terminal assistant built directly into the local developer workflow. It inspects local git diffs (both unstaged and staged) and leverages Gemini to produce:

1. **Conventional Commits:** Semantic, standardized titles and bulleted bodies (`feat:`, `fix:`, `refactor:`).
2. **Pull Request Descriptions:** Fully structured Markdown PRs complete with change breakdowns, testing verification checklists, and impact assessments.
3. **Plain-English Summaries:** Non-technical, bulleted recaps of diffs for team standups and cross-functional reviews.

---

## ✨ Key Features

- **Direct Subprocess Integration:** Interacts directly with your local git index and working tree.
- **Context-Aware Formatting:** Switches easily between Conventional Commits, PR templates, and executive summaries using the `--type` flag.
- **Staged & Unstaged Awareness:** Switch targets on the fly with `--staged`.
- **Token Protection:** Automatically detects and truncates massive diffs to prevent API token crashes while retaining critical context.
- **Rich Terminal UI:** Formatted with `rich` panels, progress spinners, and ANSI Markdown parsing.

---

## 🚀 Quickstart & Installation

### Prerequisites

- Python 3.9+
- Git installed on your system
- A Gemini API key (from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/gittldr.git
cd gittldr
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

```bash
# Windows (PowerShell):
$env:GEMINI_API_KEY="your_gemini_api_key_here"

# macOS / Linux:
export GEMINI_API_KEY="your_gemini_api_key_here"
```

---

## 💻 Usage Examples

Make edits to any file in your git repository, then run:

### 1. Generate a Conventional Commit

```bash
python gittldr.py --type commit
```

### 2. Generate a Complete Pull Request Description

```bash
python gittldr.py --type pr
```

### 3. Generate a Non-Technical Summary

```bash
python gittldr.py --type summary
```

### 4. Analyze Staged Changes Only

```bash
git add <filename>
python gittldr.py --staged --type commit
```

---

## 🛠️ Built With Nova CLI

This project was conceived, scaffolded, and brought to life using Nova CLI as the core development environment during the Build With Nova hackathon:

- **Rapid Scaffolding:** Used Nova CLI directly from the terminal to construct the CLI architecture, configure argument parsers with Click, and set up virtual environment workflows.
- **Prompt Iteration & Tuning:** Iterated through prompt designs within Nova to ensure the model generated strict Conventional Commit syntax without hallucinating nonexistent changes.
- **Edge Case Resolution:** Handled Windows character encoding exceptions in subprocess outputs and added token truncation safeguards for large repository diffs.
- **Documentation & Packaging:** Generated user guides, CLI flags documentation, and project manifests directly through the Nova interface.

---

## 📦 Tech Stack

- **CLI Framework:** Click
- **Terminal Styling:** Rich
- **AI Engine:** Google Gemini (`gemini-2.5-flash` via `google-genai` SDK)
- **Version Control:** Git Subprocess Interface
- **Development Tool:** Nova CLI
