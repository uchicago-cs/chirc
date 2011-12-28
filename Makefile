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

clean: 
	$(MAKE) clean -C src/
