#!/usr/bin/python3

import json
import sys
import click
from collections import OrderedDict


def print_empty_gradescope():
    gradescope_json = {}
    gradescope_json["score"] = 0.0
    gradescope_json["output"] = "We were unable to run the tests due to an error in your code."
    gradescope_json["visibility"] = "visible"
    gradescope_json["stdout_visibility"] = "visible"
    print(json.dumps(gradescope_json, indent=2))

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
        

@click.command(name="grade")
@click.argument('rubric_file', type=click.File())
@click.option("--report-file", type=click.File(), default="tests.json")
@click.option("--gradescope", is_flag=True)
def cmd(rubric_file, report_file, gradescope):

    def fail(msg):
        print(msg, file=sys.stderr)

        if gradescope:
            print_empty_gradescope()
            sys.exit(0)
        else:
            sys.exit(1)

    rubric = json.load(rubric_file)
    assignment = Assignment(rubric["name"], rubric["total_points"])

    for c in rubric["categories"]:
        category = Category(c["name"], c["points"])

        for sc in c["subcategories"]:
            subcategory = Subcategory(sc["cid"], sc["num_tests"])
            category.subcategories[subcategory.cid] = subcategory
            assignment.subcategories[subcategory.cid] = subcategory

        assignment.categories[category.name] = category

    try:
        results = json.load(report_file)
    except:
        fail("Error reading test results!")

    for test in results["included"]:
        if test.get("type") == "test":
            test_id = test["attributes"]["name"]
            outcome = test["attributes"]["outcome"]

            if "metadata" in test["attributes"]:
                cid = test["attributes"]["metadata"][0]["category"]
            else:
                fail("ERROR: Incorrect JSON report file (missing metadata)")

            if cid in assignment.subcategories:
                assignment.subcategories[cid].actual_num_tests += 1

                if outcome == "passed":
                    assignment.subcategories[cid].passed_tests += 1

    if gradescope:
        gradescope_json = {}
        gradescope_json["tests"] = []

        for c in assignment.categories.values():
            gs_test = {}
            gs_test["score"] = c.points_obtained
            gs_test["max_score"] = c.points
            gs_test["name"] = c.name

            gradescope_json["tests"].append(gs_test)

        gradescope_json["score"] = assignment.points_obtained
        gradescope_json["visibility"] = "visible"
        gradescope_json["stdout_visibility"] = "visible"

        print(json.dumps(gradescope_json, indent=2))
    else:
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