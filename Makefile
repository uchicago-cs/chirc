OBJS = src/main.o src/log.o
DEPS = $(OBJS:.o=.d)
CC = gcc
CFLAGS = -g3 -Wall -fpic -std=gnu99 -MMD -MP
BIN = ./chirc
LDLIBS = -pthread

.PHONY: all clean tests grade

all: $(BIN)
	
$(BIN): $(OBJS)
	$(CC) $(LDFLAGS) $(LDLIBS) $(OBJS) -o$(BIN)
	
-include $(DEPS)

clean:
	-rm -f $(OBJS) $(BIN) $(DEPS)

tests:
	@test -x $(BIN) || { echo; echo "chirc executable does not exist. Cannot run tests."; echo; exit 1; }
	python3 -m pytest tests/ --chirc-exe=$(BIN) --randomize-ports --json=tests/report.json --html=tests/report.html $(TEST_ARGS)

grade: 
	@test -s tests/report.json || { echo; echo "Test report file (tests/report.json) does not exist."; echo "Cannot generate grade without it. Make sure you run the tests first."; echo; exit 1; }
	python3 tests/grade.py --tests-file ./alltests --report-file tests/report.json
