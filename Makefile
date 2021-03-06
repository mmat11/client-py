SHELL := /bin/bash

PROTOC ?= $(shell which protoc)
GRPC_PYTHON_PLUGIN ?= $(shell which grpc_python_plugin)

PROTOS := protos/schema.proto protos/output.proto
PROTO_URLS := https://raw.githubusercontent.com/falcosecurity/falco/dev/userspace/falco/schema.proto https://raw.githubusercontent.com/falcosecurity/falco/dev/userspace/falco/output.proto
PROTO_SHAS := a1f427c114b945d0880b55058862b74015d036aa722985ca6e5474ab4ed19f69 4ce2f3e6d6ebc07a74535c4f21da73e44c6ef848ab83627b1ac987058be5ece9

PROTO_DIRS := $(dir ${PROTOS})
PROTO_DIRS_INCLUDES := $(patsubst %/, -I %, ${PROTO_DIRS})

SCHEMA_OUT_DIR := falco/schema
GRPC_OUT_DIR := falco/svc

.PHONY: protos
protos: ${PROTOS}

# $(1): the proto path
# $(2): the proto URL
# $(3): the proto SHA256
define download_rule
$(1):
	@rm -f $(1)
	@mkdir -p ${PROTO_DIRS} ${SCHEMA_OUT_DIR} ${GRPC_OUT_DIR}
	@curl --silent -Lo $(1) $(2)
	@echo $(3) $(1) | sha256sum -c
	@sed -i '/option go_package/d' $(1)
	${PROTOC} ${PROTO_DIRS_INCLUDES} --python_out=${SCHEMA_OUT_DIR} --grpc_out=${GRPC_OUT_DIR} --plugin=protoc-gen-grpc=${GRPC_PYTHON_PLUGIN} $(1)
endef
$(foreach PROTO,$(PROTOS),\
	$(eval $(call download_rule,$(PROTO),$(firstword $(PROTO_URLS)),$(firstword $(PROTO_SHAS))))\
	$(eval PROTO_URLS := $(wordlist 2,$(words $(PROTO_URLS)),$(PROTO_URLS)))\
	$(eval PROTO_SHAS := $(wordlist 2,$(words $(PROTO_SHAS)),$(PROTO_SHAS)))\
)

.PHONY: clean
clean: ${PROTO_DIRS}
	@rm -rf $^

lint:
	flake8
	isort -rc .
	black .

test:
	pytest -vv --color=yes tests/
