style:
	black *.ipynb

check-style:
	black . --check *.ipynb
	isort --check *.ipynb
	flake8 *.ipynb
	pylint *.ipynb
	pydocstyle *.ipynb