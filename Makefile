run:
	uvicorn src.app:app --reload

install:
	pip install -r requirements.txt
