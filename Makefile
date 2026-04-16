
install-dev:
	python -m pip install --upgrade pip flake8-isort flake8-commas flake8-quotes
	python -m pip install -r requirements.txt

clean-style:
	isort ./
	$(MAKE) check-style

check-style:
	isort ./ --check
	flake8 ./

tests-coverage:
	pytest --cov=brewmonitor

ci-checks: check-style tests-coverage
