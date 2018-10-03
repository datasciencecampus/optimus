#!/bin/bash
python app.py &
sleep 3
(open http://localhost:8050 || xdg-open http://localhost:8050)
