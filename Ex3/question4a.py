#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv, os


def CreateDB(files_list):
    db = {}
    db_len = 0
    max_k = -1
    for filename in files_list:
        db_len += 1
        loop_name = filename[4:-4]
        db[loop_name] = {"ranks": {}, "order": [], "seen": {}}
        with open(filename, "r") as infile:
            reader = csv.reader(infile)
            loop_max_k = 0
            for line in reader:
                if ((len(line) == 3) and (line[2] == loop_name)):
                    db[loop_name]["ranks"][line[0]] = float(line[1])
                    db[loop_name]["order"].append(line[0])
                    loop_max_k += 1
            if ((max_k == -1) or (loop_max_k < max_k)):
                max_k = loop_max_k
    # db = {
    #	'1': {
    #		'ranks': {'A': 90.0, 'C': 70.0, 'B': 80.0, 'E': 50.0, 'D': 60.0, 'G': 30.0, 'F': 40.0, 'I': 10.0, 'H': 20.0, 'J': 10.0, 'X': 10.0},
    #		'order': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'X'],
    #		'seen':  {}},
    #	'2': {
    #		'ranks': {'A': 80.0, 'C': 99.0, 'B': 11.0, 'E': 77.0, 'D': 60.0, 'G': 40.0, 'F': 65.0, 'I': 10.0, 'H': 28.0, 'J': 70.0, 'Y': 61.0},
    #		'order': ['C', 'A', 'E', 'J', 'F', 'Y', 'D', 'G', 'H', 'B', 'I'],
    #		'seen':  {}},
    #	'3': {
    #		'ranks': {'A': 87.0, 'C': 70.0, 'B': 11.0, 'E': 90.0, 'D': 99.0, 'G': 40.0, 'F': 38.0, 'I': 10.0, 'H': 61.0, 'J': 60.0, 'Z': 77.0},
    #		'order': ['D', 'E', 'A', 'Z', 'C', 'H', 'J', 'G', 'F', 'B', 'I'],
    #		'seen':  {}}
    # }
    return [db, db_len, max_k - 1]  # [db, 3, 11]


def FaginAlg(files_list, k):
    db, db_len, loop_k = CreateDB(files_list)
    if k < loop_k:
        loop_k = k  # Don't let k be out of range
    seen_all = {}
    ranks_aggr = {}
    i = 0
    stop = False
    while not stop:
        for file_num in db.keys():  # db.keys() = ['1', '2', '3']
            loop_order = db[file_num]["order"][i]
            # Update aggregation
            ranks_aggr[loop_order] = 0
            for loop_file_num in db.keys():  # db.keys() = ['1', '2', '3']
                if loop_order in db[loop_file_num]["ranks"]:
                    ranks_aggr[loop_order] += db[loop_file_num]["ranks"][loop_order]
            ranks_aggr[loop_order] /= db_len
            # Mark as seen
            db[file_num]["seen"][loop_order] = True
            # Check if also been seen at everyone else
            loop_counter = 0
            for loop_file_num in db.keys():  # db.keys() = ['1', '2', '3']
                if loop_order in db[loop_file_num]["seen"]:
                    loop_counter += 1
            if loop_counter == db_len:
                seen_all[loop_order] = ranks_aggr[loop_order]
        if len(seen_all) == loop_k:
            stop = True
        i += 1
    print "Ranked: {}".format(
        ranks_aggr)  # Ranked: {'A': 85.66666666666667, 'C': 79.66666666666667, 'B': 34.0, 'E': 72.33333333333333, 'D': 73.0, 'F': 47.666666666666664, 'J': 46.666666666666664, 'Z': 25.666666666666668}
    print "Seen all: {}".format(
        seen_all)  # Seen all: {'A': 85.66666666666667, 'C': 79.66666666666667, 'E': 72.33333333333333}
    print "Actions: {}\n".format(i * db_len)  # Actions: 15
    return sorted(ranks_aggr.items(), key=lambda x: x[1], reverse=True)[
           0:k]  # return [('A', 85.66666666666667), ('C', 79.66666666666667), ('D', 73.0)]


if __name__ == "__main__":
    files_list = []
    for filename in os.listdir("./"):
        if ((filename[:4] == "data") and (filename[-4:] == ".csv")):  # filename = "data????.csv"
            files_list.append(filename)
    if len(files_list) > 0:
        print FaginAlg(files_list, 3)  # FaginAlg(['data1.csv', 'data2.csv', 'data3.csv'], 3)
    else:
        print "[Error]\tNo input file found,\n\tThis code search for files name 'data????.csv' in the working directory..."
