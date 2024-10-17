install:
	pip3 install -r requirements.txt

clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .pytest

freeze:
	pip3 freeze > requirements.txt
