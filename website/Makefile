
install-dev:
	python -m pip install --upgrade pip flake8-isort flake8-commas flake8-quotes
	python -m pip install -r requirements.txt

clean-style:
	isort python/
	$(MAKE) check-style

check-style:
	isort python/ --check
	flake8 python/

tests:
	pytest

tests-coverage:
	pytest --cov=brewmonitor
