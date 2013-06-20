#!/bin/bash
#find . -name '*.pyc' -exec rm -rf {} \;
rm -rf ./*.pyc
rm -rf ./workers/*.pyc
# rm tmp/output
# ipcluster -n 4 > tmp/output &
# python superspider.py
