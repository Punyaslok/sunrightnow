# Sun, Right Now!

A simple web app to visualize solar data using SunPy

## Short Overview of all files

- `app.py`
    -  The main file for the app.
    -  Contains all flask config settings for the app, as well as all database implementation, and the cronjob function.
    -  Has a separate function for each client's page.
- commonfunctions.py
    - Has all Fido functions for downloading various clients' files as well as SRS files.
    - Has the overplotting function.
- plot_client.py
    - Uses functions in commonfunctions.py to plot and save imaging clients.
- conda-requirements.txt and requirements.txt
    - Contains prerequisite packages needed by dokku to run this flask app.

## Details of How the App Works

- base_url/x represents a client's page, where x = magnetogram, goes, eve, aia etc.
- The Database
    - Each class inside `app.py` corresponds to a separate table for each client in the database.
    - Each class attribute is a field in the database.
    - The class `BaseClass` is inherited by all imaging client classes.
    - For timeseries data, you may need to add or change attributes if the data which they provide changes in the future.

- The Cronjob / Scheduler
    - The cronjob uses UTC as reference timezone, and runs everyday
    - In order to know when to run each day, a list of hours is made, which is stored in the `hour_string` variable.
    - So if `hour_string = [1, 8, 15, 22]` then the job will run at `0100 hrs, 0800 hrs, 1500 hrs, 2200hrs` everyday.
    - The cronjob is called explicitly once on app startup
    - Inside `job_function`, the cronjob populates the database with entries from `start_date` to `end_date`

- Example script download
    - The `download` script inside `app.py` handles this
    - It uses the `get_text_for_imaging` function from `commonfunctions.py`, which gets the base script from `static/python_scripts/imaging_script.py` and makes modifications according to the client and provides the `.py` file for download.
    - Similarly for timeseries, `get_text_for_timeseries` is used with base script being `static/python_scripts/timeseries_script.py`