.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_pathlib_basic_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python pathlib_basic_cli.py info /home/user/file.tar.gz

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile pathlib_basic_cli.py -o pathlib_basic

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f pathlib_basic

io-check:
	@echo "I/O check not implemented for this example"
