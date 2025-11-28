.PHONY: test run compile clean io-check

test:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python -m pytest test_websocket_cli.py -v

run:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && python websocket_cli.py --mode encode --text "Hello, WebSocket!"

compile:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && depyler compile websocket_cli.py -o websocket_frame

clean:
	cd $(dir $(lastword $(MAKEFILE_LIST))) && rm -f websocket_frame

io-check:
	@echo "I/O check not implemented for this example"
