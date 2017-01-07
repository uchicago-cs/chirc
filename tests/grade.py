#!/usr/bin/python3

import argparse
import json
import sys

class Assignment(object):
    
    def __init__(self, name, points):
        self.name = name
        self.points = points
        self.categories = {}
        self.lcategories = []
        
    def add_category(self, cid, name, points):
        self.categories[cid] = (name, points)
        self.lcategories.append(cid)
    

ASSIGNMENT_1 = Assignment("Assignment 1", 50)    
ASSIGNMENT_2 = Assignment("Assignment 2", 50)    
ASSIGNMENT_3 = Assignment("Assignment 3", 50)    

ASSIGNMENTS = [ASSIGNMENT_1, ASSIGNMENT_2, ASSIGNMENT_3]

ASSIGNMENT_1.add_category("BASIC_CONNECTION", "Basic Connection", 50)

ASSIGNMENT_2.add_category("CONNECTION_REGISTRATION", "Connection Registration", 15)
ASSIGNMENT_2.add_category("PRIVMSG_NOTICE", "PRIVMSG and NOTICE", 15)
ASSIGNMENT_2.add_category("PING_PONG", "PING and PONG", 2)
ASSIGNMENT_2.add_category("MOTD", "MOTD", 3)    
ASSIGNMENT_2.add_category("LUSERS", "LUSERS", 5)
ASSIGNMENT_2.add_category("WHOIS", "WHOIS", 5)
ASSIGNMENT_2.add_category("ERR_UNKNOWN", "ERR_UNKNOWN", 2)
ASSIGNMENT_2.add_category("ROBUST", "Robustness", 3)
    
ASSIGNMENT_3.add_category("CHANNEL_JOIN", "JOIN", 5)
ASSIGNMENT_3.add_category("CHANNEL_PRIVMSG_NOTICE", "PRIVMSG and NOTICE to channels", 10)
ASSIGNMENT_3.add_category("CHANNEL_PART", "PART", 5)
ASSIGNMENT_3.add_category("CHANNEL_TOPIC", "TOPIC", 5)
ASSIGNMENT_3.add_category("MODES", "User and channel modes", 15)
ASSIGNMENT_3.add_category("AWAY", "AWAY", 2)
ASSIGNMENT_3.add_category("NAMES", "NAMES", 2)
ASSIGNMENT_3.add_category("LIST", "LIST", 2)
ASSIGNMENT_3.add_category("WHO", "WHO", 2)
ASSIGNMENT_3.add_category("UPDATE_ASSIGNMENT2", "Update Assignment 2", 2)


parser = argparse.ArgumentParser()
parser.add_argument("--tests-file", default="alltests")
parser.add_argument("--report-file", default="report.json")
parser.add_argument("--csv", action="store_true")

args = parser.parse_args()

tests = {}
all_test_ids = set()

with open(args.tests_file) as f:
    for l in f:
        category, test_id = l.strip().split(",")
        tests.setdefault(category, {})[test_id] = 0
        all_test_ids.add(test_id)

run_test_ids = set()
with open(args.report_file) as f:
    results = json.load(f)

for test in results["report"]["tests"]:
    if "call" in test:
        test_id = test["name"]
        outcome = test["outcome"]
        run_test_ids.add(test_id)
    
        if outcome == "passed":
            if "metadata" in test["call"]:
                category = test["call"]["metadata"]["category"]
            elif "metadata" in test:
                category = test["metadata"][0]["category"]
            else:
                print("ERROR: Incorrect JSON report file (missing metadata)")
                sys.exit(1)
            tests[category][test_id] = 1
    
not_run = all_test_ids.difference(run_test_ids)

if len(not_run) > 0 and not args.csv:
    print("WARNING: Missing results from {} tests (out of {} possible tests)\n".format(len(not_run), len(all_test_ids)))


scores = {}
for assignment in ASSIGNMENTS:
    scores[assignment.name] = {}
    for category in assignment.lcategories:
        num_total = len(tests[category])
        num_success = sum(tests[category].values())
        num_failed = num_total - num_success
        scores[assignment.name][category] = (num_success, num_failed, num_total)

pscores = []
for assignment in ASSIGNMENTS:
    pscore = 0.0
    if not args.csv:
        print(assignment.name)
        print("=" * 73)
        print("%-35s %-6s / %-10s  %-6s / %-10s" % ("Category", "Passed", "Total", "Score", "Points"))
        print("-" * 73)
    for cid in assignment.lcategories:
        (num_success, num_failed, num_total) = scores[assignment.name][cid]
        cname, cpoints = assignment.categories[cid]

        if num_total == 0:
            cscore = 0.0
        else:
            cscore = (float(num_success) / num_total) * cpoints

        pscore += cscore
        
        if not args.csv:
            print("%-35s %-6i / %-10i  %-6.2f / %-10.2f" % (cname, num_success, num_total, cscore, cpoints))
    if not args.csv:
        print("-" * 73)
        print("%54s = %-6.2f / %-10i" % ("TOTAL", pscore, assignment.points))
        print("=" * 73)
        print()
    pscores.append(pscore)

if args.csv:
    print(",".join([str(s) for s in pscores]))


