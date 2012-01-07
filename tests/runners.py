import HTMLTestRunner
import unittest
import tests
import sys

def find_test(obj, name):
    if isinstance(obj, unittest.suite.TestSuite):
        for t in obj:
            r = find_test(t, name)
            if r is not None:
                return r
    else:
        if isinstance(obj, tests.common.ChircTestCase) and obj._testMethodName == name:
            return obj
        else:
            return None

def get_test_list(obj):
    l = []
    if isinstance(obj, unittest.suite.TestSuite):
        for t in obj:
            l += get_test_list(t)
        return l
    else:
        if isinstance(obj, tests.common.ChircTestCase):
            return [obj]
        else:
            return []

def get_scores(result):
    alltests = get_test_list(tests.alltests)
    alltests_methods = dict([(t._testMethodName, getattr(t, t._testMethodName)) for t in alltests])

    failed_names = set([t._testMethodName for t,e in result.errors + result.failures])

    scores = {}
    for proj in tests.scores.PROJECTS:
        scores[proj.name] = {}
        for cid in proj.lcategories:
	    ctests_names = set([name for name, method in alltests_methods.items() if method.category == cid and method.points == True])
            num_total = len(ctests_names)
            num_failed = len(ctests_names & failed_names)
            num_success = num_total - num_failed
            scores[proj.name][cid] = (num_success, num_failed, num_total)
    return scores

def html_runner(html_file):
    # output to a file
    fp = file(html_file, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                verbosity = 0,
                title='chirc',
                description='Results of running all chirc unit tests'
                )
    
    # run the test
    result = runner.run(tests.alltests)
    return result

def grade_runner(csv, exe = None):
    if exe != None:
        tests.common.ChircTestCase.CHIRC_EXE = exe

    if not csv:
        stream = sys.stderr
    else:
        stream = open("/dev/null", "w")

    runner = unittest.TextTestRunner(stream = stream)
    
    # run the test
    result = runner.run(tests.alltests)

    scores = get_scores(result)

    pscores = []
    for proj in tests.scores.PROJECTS:
        pscore = 0.0
        if not csv:
            print proj.name
            print "=" * 73
            print "%-35s %-6s / %-10s  %-6s / %-10s" % ("Category", "Passed", "Total", "Score", "Points")
            print "-" * 73
        for cid in proj.lcategories:
            (num_success, num_failed, num_total) = scores[proj.name][cid]
            cname, cpoints = proj.categories[cid]

            if num_total == 0:
                cscore = 0.0
            else:
                cscore = (float(num_success) / num_total) * cpoints

            pscore += cscore
            
            if not csv:
                print "%-35s %-6i / %-10i  %-6.2f / %-10.2f" % (cname, num_success, num_total, cscore, cpoints)
        if not csv:
            print "-" * 73
            print "%54s = %-6.2f / %-10i" % ("TOTAL", pscore, proj.points)
            print "=" * 73
            print
        pscores.append(pscore)
    if csv:
        print ",".join([`s` for s in pscores])
    return result

def single_runner(test_name):
    t = find_test(tests.alltests, test_name)
    
    if t is None:
        return
    
    tests.DEBUG = True
    runner = unittest.TextTestRunner()   
    runner.run(t)
