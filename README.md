# Hospital_System_Flask_2_0

'''

## This is a Web Application developed with a goal to make Medical records sharing between doctors and patients easy.

[System Demonstration video](https://youtu.be/SzM33AO3G9U)


#### Python version 3.7.7 

## System Setup Steps:

1. Download and Install wkhtmltopdf and set an environmental variable to the installed bin directory. In this system wkhtmltopdf version 0.12.6 was used.
2. A new virtual environment is recommended for this system.
3. Go to the directory /System_2_0_1/ (stay in this directory for steps 4, 5 and 6). The system requirements files are there. Install the requirements by this terminal command =>
    pip install -r requirements_system.txt
4. Setup the Database by these terminal commands in order =>
    python databaseManager.py db init
    python databaseManager.py db migrate
    python databaseManager.py db upgrade
5. Set the initial values in the database by this terminal command =>
    python setInitialValues.py
6. Run the localhost server by this command =>
    python runFile.py
