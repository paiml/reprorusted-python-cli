.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_backup_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python backup_cli.py backup Makefile -d ./backups

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile backup_cli.py -o backup_tool

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f backup_tool && rm -rf ./backups

io-check:
	@echo "I/O check not implemented for this example"
