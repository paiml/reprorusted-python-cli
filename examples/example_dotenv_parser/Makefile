.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_dotenv_cli.py -v

run:
	@echo "Run with: python dotenv_cli.py parse .env"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile dotenv_cli.py -o dotenv_parser

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f dotenv_parser

io-check:
	@echo "I/O check not implemented for this example"
