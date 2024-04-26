import os, json, glob 
config_template = {"packages": ["numpy"], "files": {"/media_pipe/gesture/base.py": ""}}
models = glob.glob("./transcribe-asl/gesture/base_poses_hf/*.csv")
for model in models:
  model = model.replace('./transcribe-asl', '/')
  config_template["files"][model] = ""
print(json.dumps(config_template))

