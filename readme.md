# Email/Cold mail Automation tool

An open-source email automation tool/ cold outreach tool. Schedule, personalize, and send!
<br/>
<br/>
Have you ever meticulously crafted a personalized email to a potential employer or potenial collabrator and waited eagerly for a response that never arrived? It's a common scenario, and the disappointment is palpable. Creating highly personalized emails is time-consuming and often doesn't yield the desired results. Email automation offers a workaround - the ability to create semi-personalized emails, schedule them send them to multiple recipients.


## Features

* Create dynamic email templates.
* Use variables, and if statements in your email template.
* Schedule email.
* Schedule Follow-ups (follow-ups increase the chance of receiving a response from the recipient).
* Specify follow-up rule. 
* Use existing templates.

> [!WARNING]  
Don't use this service to send marketing emails or spam. It can result in your email being sent to spam or locked.

> [!NOTE]  
Stop using gmail or yahoo mail for cold outreach , both Google and yahoo actively prevents automation. Use your own domain or hotmail/outlook

> This tool makes use if Jinja2 to render the emails, so any valid Jinja syntax is acceptable


### screenshots

1. **Create unlimited email templates**
![Cold emailing tool](https://public-files.gumroad.com/wk2jt2o9mp9mp70zrglta2jidlkf)

2. **Use variables and if conditions**
![email automation tool](https://public-files.gumroad.com/jq2jpuftl5jc10oop92ji1v8gc6b)

3. **Create campaigns and follow-ups**
![Emailing tool](https://public-files.gumroad.com/r08c2gb3f33wg6zcprenqa7qfyg3)


## Example Usage

Subject
```
Feedback on Cold outreach
```

Body
```
Hello {{name}},
Hope you are doing well. I am {{from_name}} reaching out to you to
inquire about your experience using this automation platform. It 
looks like your experience with us is {% if feedback == "positive" %} 
positive {% else %} negative {% endif %}. We would be grateful, if you 
could explain a little more about your feed back.

{{from_signature}}
```

<details>

<summary>Output</summary>
Hello Rob,

Hope you are doing well. I am Paul reaching out to you to inquire about your experience using this automation platform. It looks like your experience with us is positive . We would be grateful if you could explain a little more about your feedback.

Best regards, Paul

</details>

## How it works?

 1. Configure a email id by clicking on email configuration link.
 2. Create a email template. Use Variables within enclosed brackets `{{}}` to personalize the email.
 3. Schedule the email, create followups.

## How to use
1. Follow the below steps and get it running locally or on cloud. 
2. Once done, run the app and configure your email from the dashboard.
3. create a template from template section.
4. Schedue and send


## Self hosting
If you want to self host it.

clone the repo
```
git clone https://github.com/PaulleDemon/Email-automation
```
Install python 3.8 or above

Install dependencies
```
pip install -r requirements.txt
```

add a .env file inside the email_automation folder with the following 
```
DEBUG=1
DOMAIN=""
SECRET_KEY=""
PORD_SECRET_KEY=""
REDIS_PROD_HOST=""

FIELD_ENCRYPTION_KEY=""
PROD_FIELD_ENCRYPTION_KEY=""

EMAIL_HOST="" #optional
EMAIL_HOST_USER=""#optional
EMAIL_HOST_PASSWORD="" #optional

POSTGRES_DATABASE=""
POSTGRES_USER=""
PROD_DB_PASSWORD=""
POSTGRES_PASSWORD=""
POSTGRES_HOST=""

POSTGRES_URL=""

FIREBASE_CRED_PATH=""
```
> You must fill up the values required

> You can create encryption key using the following `python manage.py generate_encryption_key`

> To generate secret key use `from django.core.management.utils import get_random_secret_key` then `get_random_secret_key()` in your python shell

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

Run celery worker:
```
celery -A email_automation worker -l info -B --scheduler django_celery_beat.schedulers:DatabaseScheduler 
```

Once you are satisfied you can build the tailwind using
```
python manage.py tailwind build
```

> Note: This tool makes use of Jinja templatig engine in the backend and nunjucks in the frontend for error checks. 

> You can use any valid Jinja syntax in the email template you are creating.

### Deployment:

If you are deploying on Render, Railway, or Digital Ocean, You will be required to fire up different services. One for web other for celery.

You can make use of Railway to deploy your own instance.

<a href="https://railway.app?referralCode=BfMDHP">
  <img src="logos/railway.png" alt="railway icon" height="50px"/>
</a>


