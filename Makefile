# Dev dependencies go here...
dev:
	pip install glob
	# sudo apt get install npm
	npm install -g serve

pyscript-config:
	python build-config.py > ./website/gesture/pyscript-config.json

website-build: pyscript-config
	cp ./transcribe-asl/gesture/base_poses_hf/*.csv ./website/media_pipe/gesture/base_poses_hf/
	cp ./transcribe-asl/gesture/base.py ./website/media_pipe/gesture/base.py

website-test:
	cd ./website && serve

# Must run in dir that we want....
dev-local:
	python -m venv venv
	source ./venv/bin/activate
	pip ./transcribe-asl/requirements.txt