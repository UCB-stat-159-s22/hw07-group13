.PHONY: env
env :
	mamba env create -f environment.yml --name aqproject
	conda activate aqproject
	python -m ipykernel install --user --name aqproject --display-name "IPython - aqproject"
