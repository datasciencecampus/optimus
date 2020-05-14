---
layout: docs
docid: "installation"
title: "Installation"
permalink: /docs/installation.html
subsections:
  - title: Install
    id: install
---

<a id="install"> </a>

optimus.py has been developed to work on both Windows and MacOS.

Please make sure Python 3.6 is installed and set in your path.  To check the Python version default for your system, run the following in command line/terminal:

```bash
# Bash
python --version
```

**_Note_**: If Python 2.x is the default Python version, but you have installed Python 3.x, your path may be setup to use `python3` instead of `python`.

To install pyGrams packages and dependencies, from the root directory (./optimus) run:

```bash
# Bash 
pip install -e .
```

This will install all the libraries and then download their required datasets.