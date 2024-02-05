#!/bin/bash

nohup python3.11 ./ai2.py > ai2.log 2>&1 &
nohup python3.11 ./orgphishing3.py > orgphishing3.log 2>&1 &
nohup python3.11 ./perphishing3.py > perphishing3.log 2>&1 &
nohup python3.11 ./orgreport.py > orgreport.log 2>&1 &
nohup python3.11 ./perreport.py > perreport.log 2>&1 &
