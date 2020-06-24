#!/bin/bash

if test -f ".pid"; then
    # shellcheck disable=SC2046
    kill -9 $(cat .pid) && rm .pid;
fi

python3 -m src.redirector.tests.tests_server &
echo $! >.pid

python3 -m unittest src.redirector.tests.tests;
# shellcheck disable=SC2046
kill -9 $(cat .pid) && rm .pid;