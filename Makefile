.PHONY: lint lint-check format format-check serve-docs build-docs build build-agent-bindings test test-cov test-unit test-integration test-watch

lint:
	pipenv run ruff check --fix icecap tests

lint-check:
	pipenv run ruff check icecap tests
	pipenv run mypy icecap

format:
	pipenv run ruff format icecap tests

format-check:
	pipenv run ruff format --check icecap tests

test:
	pipenv run pytest tests/ -v

test-cov:
	pipenv run pytest --cov=icecap --cov-branch --cov-report=xml

test-unit:
	pipenv run pytest tests/unit/ -v

test-integration:
	pipenv run pytest tests/integration/ -v

serve-docs:
	pipenv run mkdocs serve

build-docs:
	pipenv run mkdocs build

build:
	pipenv run python -m build

build-agent-bindings:
	@echo "Building agent bindings from icecap-contracts..."
	@echo "Cleaning existing bindings..."
	@if exist "icecap\agent\v1\" del /q /s "icecap\agent\v1\*" >nul 2>&1
	@echo "Clone or update contracts repo..."
	@if exist "icecap-contracts" ( \
		echo "Updating existing icecap-contracts repo..." && \
		cd icecap-contracts && git pull origin main \
	) else ( \
		echo "Cloning icecap-contracts repo..." && \
		git clone https://github.com/mora9715/icecap-contracts.git \
	)
	@echo "Compiling protobuf definitions..."
	pipenv run python -m grpc_tools.protoc --python_out=./ --pyi_out=./ --proto_path=icecap-contracts icecap/agent/v1/commands.proto
	pipenv run python -m grpc_tools.protoc --python_out=./ --pyi_out=./ --proto_path=icecap-contracts icecap/agent/v1/common.proto
	pipenv run python -m grpc_tools.protoc --python_out=./ --pyi_out=./ --proto_path=icecap-contracts icecap/agent/v1/events.proto
	@echo "Creating Python package..."
	@if not exist "icecap\agent\v1\__init__.py" echo. > "icecap\agent\v1\__init__.py"
	@echo "Agent bindings built successfully!"
