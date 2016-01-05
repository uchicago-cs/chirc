#!/usr/bin/python3

import argparse
import json

class Project(object):
    
    def __init__(self, name, points):
        self.name = name
        self.points = points
        self.categories = {}
        self.lcategories = []
        
    def add_category(self, cid, name, points):
        self.categories[cid] = (name, points)
        self.lcategories.append(cid)
    

PROJ_1A = Project("Project 1a", 50)    
PROJ_1B = Project("Project 1b", 100)    
PROJ_1C = Project("Project 1c", 100)    

PROJECTS = [PROJ_1A, PROJ_1B, PROJ_1C]

PROJ_1A.add_category("BASIC_CONNECTION", "Basic Connection", 50)

PROJ_1B.add_category("CONNECTION_REGISTRATION", "Connection Registration", 35)
PROJ_1B.add_category("PRIVMSG_NOTICE", "PRIVMSG and NOTICE", 30)
PROJ_1B.add_category("PING_PONG", "PING and PONG", 2.5)
PROJ_1B.add_category("MOTD", "MOTD", 5)    
PROJ_1B.add_category("LUSERS", "LUSERS", 10)
PROJ_1B.add_category("WHOIS", "WHOIS", 10)
PROJ_1B.add_category("ERR_UNKNOWN", "ERR_UNKNOWN", 2.5)
PROJ_1B.add_category("ROBUST", "Robustness", 5)
    
PROJ_1C.add_category("CHANNEL_JOIN", "JOIN", 15)
PROJ_1C.add_category("CHANNEL_PRIVMSG_NOTICE", "PRIVMSG and NOTICE to channels", 15)
PROJ_1C.add_category("CHANNEL_PART", "PART", 10)
PROJ_1C.add_category("CHANNEL_TOPIC", "TOPIC", 10)
PROJ_1C.add_category("MODES", "User and channel modes", 25)
PROJ_1C.add_category("AWAY", "AWAY", 5)
PROJ_1C.add_category("NAMES", "NAMES", 5)
PROJ_1C.add_category("LIST", "LIST", 5)
PROJ_1C.add_category("WHO", "WHO", 5)
PROJ_1C.add_category("UPDATE_1B", "UPDATE_1B", 5)


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
        category = test["call"]["metadata"]["category"]
        test_id = test["name"]
        outcome = test["outcome"]
        run_test_ids.add(test_id)
    
        if outcome == "passed":
            tests[category][test_id] = 1
    
not_run = all_test_ids.difference(run_test_ids)

if len(not_run) > 0 and not args.csv:
    print("WARNING: Missing results from {} tests (out of {} possible tests)\n".format(len(not_run), len(all_test_ids)))


scores = {}
for proj in PROJECTS:
    scores[proj.name] = {}
    for category in proj.lcategories:
        num_total = len(tests[category])
        num_success = sum(tests[category].values())
        num_failed = num_total - num_success
        scores[proj.name][category] = (num_success, num_failed, num_total)

pscores = []
for proj in PROJECTS:
    pscore = 0.0
    if not args.csv:
        print(proj.name)
        print("=" * 73)
        print("%-35s %-6s / %-10s  %-6s / %-10s" % ("Category", "Passed", "Total", "Score", "Points"))
        print("-" * 73)
    for cid in proj.lcategories:
        (num_success, num_failed, num_total) = scores[proj.name][cid]
        cname, cpoints = proj.categories[cid]

        if num_total == 0:
            cscore = 0.0
        else:
            cscore = (float(num_success) / num_total) * cpoints

        pscore += cscore
        
        if not args.csv:
            print("%-35s %-6i / %-10i  %-6.2f / %-10.2f" % (cname, num_success, num_total, cscore, cpoints))
    if not args.csv:
        print("-" * 73)
        print("%54s = %-6.2f / %-10i" % ("TOTAL", pscore, proj.points))
        print("=" * 73)
        print()
    pscores.append(pscore)

if args.csv:
    print(",".join([str(s) for s in pscores]))


