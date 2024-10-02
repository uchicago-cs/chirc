import json

import pytest
import os.path

def pytest_addoption(parser):
    parser.addoption("--chirc-category", action="store", metavar="CATEGORY_ID",
        help="only run tests in category CATEGORY_ID.")
    parser.addoption("--chirc-rubric", action="append", metavar="RUBRIC_FILE",
                     help="only run the tests in this rubric file")
    parser.addoption("--chirc-exe", action="store", metavar="CHIRC_EXE", default="../build/chirc",
        help="set location of chirc executable")       
    parser.addoption("--chirc-loglevel", action="store", type=int, default=0, metavar="LOGLEVEL",
        help="set log level in chirc to LOGLEVEL (-1: -q, 0: normal, 1: -v, 2: -vv).")
    parser.addoption("--chirc-port", action="store", type=int, default=-1,
        help="port to run chirc on (use -1 to use a random port in each test)")
    parser.addoption("--chirc-external-port", action="store", type=int,
                     help="Do not launch chirc, and instead connect to chirc on this port")
    parser.addoption("--generate-alltests-file", action="store", type=str, default=None,
                     help="Generate file with all the test categories and names")


def pytest_sessionstart(session):
    session.rubric_categories = None
    rubric_files = session.config.option.chirc_rubric
    if rubric_files is not None:
        session.rubric_categories = set()
        for rubric_file in rubric_files:
            if not os.path.exists(rubric_file):
                pytest.exit("No such rubric file: {}".format(rubric_file))

            with open(rubric_file) as f:
                rubric = json.load(f)
                for c in rubric["categories"]:
                    for sc in c["subcategories"]:
                        session.rubric_categories.add(sc["cid"])

def pytest_collection_finish(session):
    if session.config.option.chirc_external_port is not None and len(session.items) > 1:
        pytest.exit("Cannot use --use-external-chirc when running more than one test.")

    if session.config.option.generate_alltests_file is not None:
        with open(session.config.option.generate_alltests_file, "w") as f:
            for item in session.items:
                category_marker = item.get_closest_marker("category")
                if category_marker is not None:
                    category = category_marker.args[0]
                    f.write("{},{}\n".format(category, item.nodeid))


def pytest_runtest_setup(item):
    rubric_categories = item.session.rubric_categories
    only_category = item.config.getoption("--chirc-category")
    if only_category is not None or rubric_categories is not None:
        category_marker = item.get_closest_marker("category")
        if category_marker is not None:
            category = category_marker.args[0]
            if only_category is not None and category != only_category:
                pytest.skip("Only running tests in category {}".format(only_category))
            elif rubric_categories is not None and category not in rubric_categories:
                pytest.skip("Only running tests in categories {}".format(", ".join(rubric_categories)))


def pytest_json_runtest_metadata(item, call):
    category = item.get_closest_marker("category").args[0]

    return {'category': category}