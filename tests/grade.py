#!/usr/bin/python3

import json
import sys
import click
from collections import OrderedDict

class Subcategory:
    def __init__(self, cid, expected_num_tests):
        self.cid = cid
        self.expected_num_tests = expected_num_tests
        self.actual_num_tests = 0
        self.passed_tests = 0

class Category:

    def __init__(self, name, points):
        self.name = name
        self.points = points
        self.subcategories = OrderedDict()

    @property
    def num_tests(self):
        return sum(sc.expected_num_tests for sc in self.subcategories.values())

    @property
    def passed_tests(self):
        return sum(sc.passed_tests for sc in self.subcategories.values())

    @property
    def points_obtained(self):
        return (self.passed_tests / self.num_tests) * self.points

class Assignment:
    
    def __init__(self, name, points):
        self.name = name
        self.points = points
        self.categories = OrderedDict()
        self.subcategories = OrderedDict()

    @property
    def points_obtained(self):
        return sum(c.points_obtained for c in self.categories.values())
        

"""    
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
"""

@click.command(name="grade")
@click.argument('rubric_file', type=click.File())
@click.option("--report-file", type=click.File(), default="tests.json")
def cmd(rubric_file, report_file):

    rubric = json.load(rubric_file)
    assignment = Assignment(rubric["name"], rubric["total_points"])

    for c in rubric["categories"]:
        category = Category(c["name"], c["points"])

        for sc in c["subcategories"]:
            subcategory = Subcategory(sc["cid"], sc["num_tests"])
            category.subcategories[subcategory.cid] = subcategory
            assignment.subcategories[subcategory.cid] = subcategory

        assignment.categories[category.name] = category

    results = json.load(report_file)

    for test in results["included"]:
        if test.get("type") == "test":
            test_id = test["attributes"]["name"]
            outcome = test["attributes"]["outcome"]

            #import pprint
            #pprint.pprint(test)
            if "metadata" in test["attributes"]:
                cid = test["attributes"]["metadata"][0]["category"]
            else:
                print("ERROR: Incorrect JSON report file (missing metadata)")
                sys.exit(1)

            if cid in assignment.subcategories:
                assignment.subcategories[cid].actual_num_tests += 1

                if outcome == "passed":
                    assignment.subcategories[cid].passed_tests += 1

    print(assignment.name)
    print("=" * 73)
    print("%-35s %-6s / %-10s  %-6s / %-10s" % ("Category", "Passed", "Total", "Score", "Points"))
    print("-" * 73)
    for c in assignment.categories.values():
        print("%-35s %-6i / %-10i  %-6.2f / %-10.2f" % (c.name, c.passed_tests, c.num_tests, c.points_obtained, c.points))
    print("-" * 73)
    print("%54s = %-6.2f / %-10i" % ("TOTAL", assignment.points_obtained, assignment.points))
    print("=" * 73)
    print()

if __name__ == "__main__":
    cmd()