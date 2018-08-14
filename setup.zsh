#!/usr/bin/env zsh

local -a help all py ft
zparseopts h=help   -help=help\
           a=all    -all=all\
           p=py     -py=py\
           f=ft     -ft=ft


#-- Functions -------------------------------------------------------------------



help () {
  echo "
    -*- o p t i m u s -*-
    A pipeline for classifying free-text strings
    Flags:
      -h --help       prints this message
      -p --py         prepare the python environment without fastText
      -f --ft         install fastText from the git repo
      -a --all        same as -pf
  "
}


py () {
  echo "** Installing required python modules"
  echo "-- If any errors occur during installation please check setup.log"

  # checking that the system is running python 3 [dependency]
  [[ -n $(command -v python3) ]] || (echo "No python 3 interpreter" && exit)
  [[ -n $(command -v pip3) ]] && alias pip='pip3'

  [[ -n $(command -v pip) ]] && pip install -r requirements.txt 1>setup.log
}


ft () {
  echo "** Installing fasttext"
  echo "-- If any errors occur during installation please check setup.log"

  # Check that we have all the required tools to build fastText
  # I'm going to ignore git and assume nobody is doing 'download' from github
  [[ -n $(command -v cmake) ]] || (echo "Please install cmake first" && exit)
  [[ -n $(command -v make)  ]] || (echo "Please install make first"  && exit)
  [[ -n $(command -v pip3)  ]] &&  alias pip='pip3'
  [[ -n $(command -v pip)   ]] || (echo "PIP not found in path"      && exit)


  git clone https://github.com/facebookresearch/fasttext 1>/dev/null 2>&1
  cd fasttext
  pip install . 1>setup.log
  cd ../ && rm -rf fasttext 1>setup.log
}


# do everything
all () {
  py
  ft
}


#-- Runtime ---------------------------------------------------------------------

[[ -n $py  ]] && py
[[ -n $ft  ]] && ft
[[ -n $all ]] && all

# catch all for no arguments -- prints help
[[ -z $(echo $py $ft $all) || -n $help ]] && help

# remove the log on successful completion
[[ -a setup.log ]] && echo "** Cleaning up installation" && rm setup.log
