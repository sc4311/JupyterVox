#!/bin/ash

# a short script to test all files in test_cases/

for file in ./test_cases/*
do
    # test with the test case
    echo "Testing file $file"
    python test.py -f $file 1>temp.txt 2>&1

    # check if all correct
    correctCnt=`grep "Correct/Total" temp.txt | cut -d ' ' -f 2 | cut -d "/" -f 1`
    totalCnt=`grep "Correct/Total" temp.txt | cut -d ' ' -f 2 | cut -d "/" -f 2`

    if [ "$correctCnt" -ne "$totalCnt" ];
    then
    	echo "File $file has incorrect statements"
    fi
done
