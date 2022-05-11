.PHONY: env
env :
	mamba env create -f environment.yml -p ~/envs/aqproject
	bash -ic 'conda activate aqproject;python -m ipykernel install --user --name aqproject --display-name "IPython - aqproject"'

all:
	bash -ic 'conda activate aqproject'
	jupyter execute ExplorationAndVisualization.ipynb MainAnalysis.ipynb Main.ipynb

.PHONY: clean
clean:
	rm -f $(wildcard figures/*.png)
	# don't want to remove *.gif or *.GeoJSON because these take a really long time 
    