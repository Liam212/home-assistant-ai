deps:
	@python3 -m venv .venv && \
	  . .venv/bin/activate && \
		pip3 install -r requirements.txt

run:
	@. .venv/bin/activate && \
	python3 main.py "$(PROMPT)"

run-llama2-model:
	ollama run llama2:7b-chat


