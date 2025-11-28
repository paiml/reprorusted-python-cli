.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_file_read_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo "hello world" | python file_read_cli.py count /dev/stdin

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile file_read_cli.py -o file_read

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f file_read

io-check:
	@echo "I/O check not implemented for this example"
