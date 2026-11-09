install:
	pip install -e ".[api,dev]"
test:
	pytest -q
demo:
	python -m engagent run "I need a lightweight aluminium wall bracket for a robotic arm, 25 kg payload, 300 mm from the wall, max deflection 1 mm" --out runs/demo
api:
	uvicorn engagent.api.main:app --reload
