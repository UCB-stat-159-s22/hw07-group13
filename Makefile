.PHONY: env
env :
	mamba env create -f environment.yml -p ~/envs/aqproject
	bash -ic 'conda activate aqproject;python -m ipykernel install --user --name aqproject --display-name "IPython - aqproject"'
