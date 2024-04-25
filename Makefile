# Dependencies go here...
dev:
	pip install glob

pyscript-config: dev
	python build-config.py > ./website/media_pipe/gesture/pyscript-config.json

website-build: pyscript-config
	cp ./transcribe-asl/gesture/base_poses_hf/*.csv ./website/gesture/base_poses_hf/
	cp ./transcribe-asl/gesture/base.py ./website/media_pipe/gesture/base.py