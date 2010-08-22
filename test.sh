#!/bin/bash

# we only test the return codes
function ok { echo; echo shoot $*; ./bin/shoot $*; [ $? -ne 0 ] && echo 'TESTS FAILED' && exit; }
function fail { echo; echo shoot $*; ./bin/shoot $*; [ $? -ne 2 ] && echo 'TESTS FAILED' && exit; }

fail
ok --calibrate 20000 360 0
ok --reset
ok --move 0
ok --move 50
ok --move +50
ok --move -100
ok --move +50 --speed 3000
ok --move 0 --duration 2.0
ok --move 50 --maxrange 50.1
ok --resolution=10.1 --move=-5
ok --resolution 10.1 -m +5.1
fail --resolution 10.1 -m 5.1 --maxrange 5.09999
ok --resolution 10.1 -m -5.1 -p 1
fail --resolution 10.1 -m +5.1 -p 3.1
ok --resolution 10.1 -m -5.1 --speed 1.0
ok --resolution 10.1 -m +5.1 --duration 1.0

# rail
ok --resolution 17.2 -b 1.0 -p 3 --manual

echo "TEST SUCCEEDED"
