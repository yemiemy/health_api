# Health In Palms

## Setting Up Dev Environment
### General OS
1. Create a python virtual environment
2. Activate the virtual environment
3. Install dependencies from the `requirements.txt` file
    - `pip install -r requirements.txt`
4. Set up redis (Check resources to set it up for your specific environment).
5. Set up PostgreSQL db. Create a DB and name it `health_db`
6. Create a `health_api_config.json` file that contains all the settings variables. Refer to the health_api/settings/base.py file for more details.

### MacOS
1. Start redis server
    - `brew services start redis`

### Setting up preliminaries
1. Run migrations
    - `python manage.py makemigrations`
    - `python manage.py migrate`
2. Create a superuser
    - `python manage.py create_super_user`
3. Start celery 
    - `python -m celery -A health_api worker`
4. Start dev server
    - `python manange.py runserver`