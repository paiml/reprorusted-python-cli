.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_env_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python env_cli.py list --prefix PATH

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile env_cli.py -o env_manager

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f env_manager

io-check:
	@echo "I/O check not implemented for this example"
