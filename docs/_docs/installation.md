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

Firstly the user should clone the git repository
```
git clone https://github.com/datasciencecampus/optimus.git

```

Within the repo is a file named `setup.zsh`. This is a command line tool to
install all of the other things you need. For help using this, invoke the script
as

``` bash
Bash
. setup.zsh -h
```

This script allows you to download the [FastText wikipedia word
embeddings](https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md)
model and places it in the optimus directory. If your project is elsewhere and
you are not working in optimus directly then it is recommended to use this script to
download the model and then you can move it to be local to your working directory.
