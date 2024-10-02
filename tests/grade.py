#!/usr/bin/env python

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
    def __init__(self, assignment, cid, expected_num_tests):
        self.assignment = assignment
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
@click.argument('rubric_files', type=click.File(), nargs=-1)
@click.option("--report-file", type=click.File(), default="tests.json")
@click.option("--gradescope", is_flag=True)
def cmd(rubric_files, report_file, gradescope):

    def fail(msg):
        print(msg, file=sys.stderr)

        if gradescope:
            print_empty_gradescope()
            sys.exit(0)
        else:
            sys.exit(1)

    assignments = []
    subcategories = {}
    for rubric_file in rubric_files:
        rubric = json.load(rubric_file)
        assignment = Assignment(rubric["name"], rubric["total_points"])

        for c in rubric["categories"]:
            category = Category(c["name"], c["points"])

            for sc in c["subcategories"]:
                if sc["cid"] in subcategories:
                    fail(f"Repeated subcategory: {sc['cid']}")

                subcategory = Subcategory(assignment, sc["cid"], sc["num_tests"])
                category.subcategories[subcategory.cid] = subcategory
                assignment.subcategories[subcategory.cid] = subcategory

                subcategories[sc["cid"]] = subcategory

            assignment.categories[category.name] = category

        assignments.append(assignment)

    try:
        results = json.load(report_file)
    except:
        fail("Error reading test results!")

    for test in results["tests"]:
        test_id = test["nodeid"]
        outcome = test["outcome"]

        if "metadata" in test:
            cid = test["metadata"]["category"]
        else:
            fail("ERROR: Incorrect JSON report file (missing metadata)")

        if cid in subcategories:
            subcategories[cid].assignment.subcategories[cid].actual_num_tests += 1

            if outcome == "passed":
                subcategories[cid].assignment.subcategories[cid].passed_tests += 1

    if gradescope:
        gradescope_json = {}
        gradescope_json["tests"] = []

        total_points_obtained = 0
        total_points_possible = 0
        for assignment in assignments:
            for c in assignment.categories.values():
                gs_test = {}
                gs_test["score"] = c.points_obtained
                gs_test["max_score"] = c.points
                gs_test["name"] = c.name

                total_points_obtained += c.points_obtained
                total_points_possible += c.points

                gradescope_json["tests"].append(gs_test)

        gradescope_json["score"] = total_points_obtained
        gradescope_json["visibility"] = "visible"
        gradescope_json["stdout_visibility"] = "visible"

        print(json.dumps(gradescope_json, indent=2))
    else:
        total_points_obtained = 0
        total_points_possible = 0
        for assignment in assignments:
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

            total_points_obtained += assignment.points_obtained
            total_points_possible += assignment.points

        if len(assignments) > 1:
            print(f"{'GRAND TOTAL':>54} = {total_points_obtained:-6.2f} / {total_points_possible}")

if __name__ == "__main__":
    cmd()