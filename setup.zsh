#!/usr/bin/env zsh

set -e

local -a help all py ft
zparseopts h=help   -help=help\
           a=all    -all=all\
           p=py     -py=py\
           f=ft     -ft=ft\
           d=dl     -dl=dl


#-- Functions -------------------------------------------------------------------
help () {
  echo "
    -*- o p t i m u s -*-
    A pipeline for classifying free-text strings
    Flags:
      -h --help       prints this message
      -p --py         prepare the python environment without fastText
      -f --ft         install fastText from the git repo
      -d --dl         download the wikipedia model for fasttext local to optimus
      -a --all        same as -pfd
  "
}


py () {
  echo "** Installing required python modules"

  # checking that the system is running python 3 [dependency]
  [[ -n $(command -v python3) ]] || (echo "No python 3 interpreter" && exit)
  [[ -n $(command -v pip3) ]] && alias pip='pip3'

  [[ -n $(command -v pip) ]] && pip install -r requirements.txt 1>setup.log
}


ft () {
  echo "** Installing fasttext"

  # Check that we have all the required tools to build fastText
  # I'm going to ignore git and assume nobody is doing 'download' from github
  [[ -n $(command -v pip3)  ]] &&  alias pip='pip3'
  [[ -n $(command -v pip)   ]] || (echo "PIP not found in path"      && exit)


  git clone https://github.com/facebookresearch/fasttext 1>/dev/null 2>&1
  cd fasttext
  pip install . 1>setup.log
  cd ../ && rm -rf fasttext 1>setup.log
}


dl () {
  [[ -a models/wiki.en.bin ]] && echo "Model already exists, exiting" && exit

  [[ -a './models/' ]] ||  mkdir models
  cd models

  set url="https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki.en.zip"
  [[ -n $(command -v curl) ]] && \
    curl -o wiki.en.zip $url ||\
    wget $url

  [[ -N $(command -v unzip) ]] &&\
    unzip wiki.en.zip ||\
    (echo "No unzip tool, exiting" && exit)

  cd ..
}


# do everything
all () {
  py
  ft
  dl
}


#-- Runtime ---------------------------------------------------------------------
echo "-- If any errors occur during installation please check setup.log"

[[ -n $py  ]] && py
[[ -n $ft  ]] && ft
[[ -n $dl  ]] && dl
[[ -n $all ]] && all

# catch all for no arguments -- prints help
[[ -z $(echo $py $ft $dl $all) || -n $help ]] && help

# remove the log on successful completion
[[ -a setup.log ]] && echo "** Cleaning up installation" && rm setup.log
