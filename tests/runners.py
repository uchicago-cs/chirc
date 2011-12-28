import HTMLTestRunner
import unittest
import tests

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

def get_scores():
    pass

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

def single_runner(test_name):
    t = find_test(tests.alltests, test_name)
    
    if t is None:
        return
    
    tests.DEBUG = True
    runner = unittest.TextTestRunner()   
    runner.run(t)