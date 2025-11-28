.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_cron_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python cron_cli.py "*/15 * * * *"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile cron_cli.py -o cron_validator

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f cron_validator

io-check:
	@echo "I/O check not implemented for this example"
