# Analysis
Repository for performing analysis and visualising our scraping results

## Getting started
After cloning this repository, there are two options to deploy the streamlit application: via Docker or directly on your machine.

### Running directly on host machine
Create a venv in the folder of the repository using:
`python -m venv venv`

To activate the venv, enter the following command:

`venv\Scripts\activate` if you're on Windows

`source venv/bin/activate` on Unix

Afterwards, install all requirements:

`pip install -r requirements_linux.txt` on Unix 

`pip install -r requirements_windows.txt` on Windows

Also, make sure you have set the following environment variables:
* MONGO_HOST (hostname of the MongoDB instance where the data is fetched, the standard port 27017 is assumed)
* MONGO_INITDB_ROOT_USERNAME (username for the MongoDB instance)
* MONGO_INITDB_ROOT_PASSWORT (password for the MongoDB instance)

Then, the application can be deployed on the host machine with the following command:

`streamlit run app.py`

A window in your standard browser pops up displaying the dashboard. The website is available under `http://localhost:8501/`

### Running with Docker
First you have to build docker image with the command `docker build -t analysis .`
Afterwards, you can start the container with the command 

`docker run -e MONGO_HOST=<mongodb_host> -e MONGO_INITDB_ROOT_USERNAME=<username> -e MONGODB_INITDB_ROOT_PASSWORD=<password> -p 8501:8501 analysis`

The streamlit dashboard is then accessible under `<hostname>:8501`. 

## Developer documentation
All analyses are implemented in the classes contained in the analyzers module. They all correspond to the data source. To make the analysis available to the user, it has to be registered in the constant `ANALYSES_BY_DATA_SOURCE`. Here you give the name of the method as the key and a description for the user as the value.  