.PHONY: build

build:
	docker build -t harrischu/auto_label:v1 .

push:
	docker push harrischu/auto_label:v1
