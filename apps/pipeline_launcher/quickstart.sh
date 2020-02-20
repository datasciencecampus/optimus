#!/bin/bash
pip3 install -r requirements
cd ..
cd ..
python3 app.py &
sleep 10
(open http://localhost:8050 || xdg-open http://localhost:8050)
