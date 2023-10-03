"""
resused functionss
"""

def get_name_from_email(email):
    name, domain = email.split('@')
    return name.replace('.', ' ').strip().capitalize()