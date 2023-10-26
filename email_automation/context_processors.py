
import environ

env = environ.Env()
environ.Env.read_env()


def secrets(request):
    
    return {"gtag": env.get_value('GOOGLE_ANALYTICS', default='')}