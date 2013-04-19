FAST ?= 0
RANDOM_PORTS ?= 1

all: chirc

.PHONY: chirc tests
     
chirc: 
	$(MAKE) -C src/

tests: chirc
	nosetests tests/

htmltests: chirc
	python -c "import tests.runners; tests.runners.html_runner('report.html')"
	
singletest: chirc
	python -c "import tests.runners; tests.runners.single_runner('$(TEST)')" 

grade: chirc
	python -c "import tests.runners; tests.runners.grade_runner(csv=False, randomize_ports=$(RANDOM_PORTS), fast=$(FAST))"

clean: 
	$(MAKE) clean -C src/
