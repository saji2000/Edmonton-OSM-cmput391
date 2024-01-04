# Paths to files
# test cases
TESTDIR=./test

# test files
TESTS = t1.txt


test:
	@echo "\nTesting ... "
	@for test in `find ${TESTDIR} -name 'test*.py'`; do \
		python3 $$test ; \
	done

clean:
	@echo "Removing output of tests: rm -f $(TESTDIR)/*output.txt"
	rm -f $(TESTDIR)/*output.txt

