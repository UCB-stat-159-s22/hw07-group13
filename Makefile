.PHONY: env
env :
	mamba env create -f environment.yml --name aqproject
	bash -ic 'conda activate aqproject;python -m ipykernel install --user --name aqproject --display-name "IPython - aqproject"'

all:
	bash -ic 'conda activate aqproject'
	jupyter execute ExplorationAndVisualization.ipynb MainAnalysis.ipynb modelling.ipynb Main.ipynb

.PHONY: clean
clean:
	rm -f $(wildcard figures/*.png)
	rm -f $(wildcard data/*.pkl)
	rm -f $(wildcard tables/*.csv)
	#
	# don't want to remove *.gif or *.GeoJSON because these take a really long time 
    