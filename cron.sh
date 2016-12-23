#!/bin/bash
cd $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source venv/bin/activate
python run.py "$@" > last_run.log