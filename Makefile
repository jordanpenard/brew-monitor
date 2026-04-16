
install-dev:
	python -m pip install --upgrade pip ruff
	python -m pip install -r requirements.txt

clean-style:
	ruff check --fix .
	$(MAKE) check-style

check-style:
	ruff check .

ci-checks: check-style