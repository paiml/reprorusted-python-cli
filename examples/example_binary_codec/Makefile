.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_binary_codec_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python binary_codec_cli.py hex encode "Hello"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile binary_codec_cli.py -o binary_codec

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f binary_codec

io-check:
	@echo "I/O check not implemented for this example"
