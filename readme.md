# Email Automation tool

You can use the site at [https://peckspace.com](https://peckspace.com) 

or

clone the repo
```
git clone https://github.com/PaulleDemon/Email-automation
```

Install dependencies
```
pip install -r requirements.txt
```

add a .env file inside the email_automation folder with the following 
```
DEBUG=0
DOMAIN=""
SECRET_KEY=""
REDIS_PROD_HOST=""
FIELD_ENCRYPTION_KEY="" # for encrypting
```
> You must fill up the values required

Run database creation queries using
```
python manage.py migrate
```

now run the website using 
```
python manage.py runserver
```

The project uses tailwind so, when running locally use
```
python manage.py tailwind start
```

Once you are satisfied you can build the tailwind using
```
python manage.py tailwind build
```