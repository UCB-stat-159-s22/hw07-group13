# Exploring the Air Quality of the San Francisco Bay Area using OpenAQ #
***
This repo houses the materials for a reproducible project report exploring air quality in the San Francisco Bay Area. Using the publicly-accessible data on [OpenAQ](https://openaq.org/#/), we explored and visualized the air quality on the days surrounding the Bay Area's infamous "Dark Day" (September 9th, 2020), and used multiple statistical learning techniques to develop a potential model for predicting future "dark days" and to predict the amount of fine particulate matter (PM<sub>2.5</sub>) in the air given the presence of other air pollutants, as it is a particularly dangerous  


__Binder Link__: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/UCB-stat-159-s22/hw07-group13/HEAD?labpath=Main.ipynb)

__GitHub Pages Link__: https://ucb-stat-159-s22.github.io/hw07-group13/
***
## Installation ##

Start by using the following Make commands in your terminal:

- To create the `aqproject` virtual environment: `make env` 
- To install the `aqtools` module, navigate to the `aqtools` file and enter: `pip install .`
- To remove any previous figure or data files from the project directory: `make clean`
- To execute all of the Jupyter Notebooks and create the figures and data for the report: `make all`

***
## Testing and Automation ##

To test the data, enter the following commands in your terminal:

- To activate the project's virtual environment: `conda activate aqproject` 
- To run all tests on the functions used for visualization and data analysis: `pytest aqtools` 

***