#!/bin/bash
pip install -r requirements
python app.py &
sleep 10
(open http://localhost:8050 || xdg-open http://localhost:8050)
