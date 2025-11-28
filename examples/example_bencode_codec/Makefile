.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_bencode_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && echo '{"key": "value"}' | python bencode_cli.py -e -

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile bencode_cli.py -o bencode_codec

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f bencode_codec

io-check:
	@echo "I/O check not implemented for this example"
