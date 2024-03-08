import sys
import os
import os.path
import csv
from datetime import datetime
from collections import Counter
import operator

try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

if not os.path.exists('3sets'):
    os.makedirs('3sets')

path = "Data/{}_sprint.csv".format(repo)
print("\nREPO: {}".format(repo))
print("Task: Split dataset\n")

ach_key_order = ['low', 'balanced', 'high']
qua_key_order = ['no', 'minor', 'moderate', 'major']

# train/valid/test
splitRatio = (60,20,20)

with open(path) as csvFile:
    csvReader = csv.reader(csvFile, delimiter=',')
    csvList = list(csvReader)
    data = csvList[1:]

    # e.g. 2017-10-02 21:11:00
    # dateTimeCode = '%Y-%m-%d %H:%M:%S'
    dataLength = len(data)

    trainSize = (dataLength * splitRatio[0]) // 100
    validSize = (dataLength * splitRatio[1]) // 100
    testSize = (dataLength * splitRatio[2]) // 100

    if not (trainSize + validSize + testSize) == dataLength:
        trainSize = trainSize + (dataLength - (trainSize + validSize + testSize))

    print ("Total sprints: {}".format(dataLength))
    print ("Split ratio: {}".format(splitRatio))
    print ("Train size: {}, validate size: {}, test size: {}".format(trainSize, validSize, testSize))
 
    # save train/valid/test size as text file
    with open('3sets/{}_3sets_size.txt'.format(repo), 'w') as f:
        f.write('{}:{}:{}\n'.format(trainSize, validSize, testSize))

    countRow = 0

    labelFile = "3sets/{}_3sets.tsv".format(repo)
    if os.path.exists(labelFile):
        os.remove(labelFile)

    with open(labelFile, 'a') as tsvFile:
        tsvFile.write("ID\tBID\tSID\tLabel\n")
        for row in data:
            countRow = countRow + 1
            if countRow <= trainSize:
                tsvFile.write("{}\t{}\t{}\t{}".format(countRow, row[0], row[1], "train"))
            elif countRow > trainSize and countRow <= validSize + trainSize:
                tsvFile.write("{}\t{}\t{}\t{}".format(countRow, row[0], row[1], "valid"))
            elif countRow > validSize and countRow <= testSize + validSize + trainSize:
                tsvFile.write("{}\t{}\t{}\t{}".format(countRow, row[0], row[1], "test"))
            if not countRow == len(data):
                tsvFile.write("\n")

    print("Write File [{}_3sets.tsv] successfully\n".format(repo))
            