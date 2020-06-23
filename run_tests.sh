#!/bin/bash
python3 -m tests_server &
echo $! >.pid
python3 -m unittest tests && kill -9 $(cat .pid) && rm .pid