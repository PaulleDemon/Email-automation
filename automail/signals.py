import json
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_delete, post_delete
from django_celery_beat.models import PeriodicTask, ClockedSchedule, IntervalSchedule

from utils.tasks import send_html_mail_celery
from .models import EmailCampaignTemplate, EmailConfiguration, EmailCampaign


def deletePeriodicTask(id):
    tasks = PeriodicTask.objects.filter(name=f'email_{id}')
    tasks.update(enabled=False)      
    tasks.delete()

@receiver(post_save, sender=EmailCampaignTemplate)
def schedule_email(instance, sender, created, *args, **kwargs):

    

    if instance.scheduled:
        
        tasks = PeriodicTask.objects.filter(name=f'email_{instance.id}')
        tasks.update(enabled=False)      
        tasks.delete()

        if not instance.schedule:
            raise ValidationError("Schedule not found", code=400)

        schedule_start = ClockedSchedule.objects.create(clocked_time=instance.schedule)

        PeriodicTask.objects.create(name=f'email_{instance.id}', clocked=schedule_start, one_off=True, 
                                        kwargs=json.dumps({'id': instance.id}), 
                                        task='run_schedule_email')


    else:
        deletePeriodicTask(instance.id)

    if instance.completed:
        deletePeriodicTask(instance.id)



@receiver(post_save, sender=EmailCampaign)
def disable_email_campaign(instance, sender, created, *args, **kwargs):
    
    if instance.discontinued == True:
        for x in EmailCampaignTemplate.objects.filter(campaign=instance.id): 
            tasks = PeriodicTask.objects.filter(name=f'email_{x.id}')
            tasks.update(enabled=False)      
            tasks.delete()


@receiver(pre_delete, sender=EmailCampaignTemplate)
def remove_scheduled_mail(sender, instance, **kwargs):

    try: 
        task = PeriodicTask.objects.get(name=f'email_{instance.id}')
        task.enabled = False
        task.save()
        task.delete()

    except (PeriodicTask.DoesNotExist):
        pass


@receiver(post_save, sender=EmailConfiguration)
def inform_user(sender, instance, created, *args, **kwargs):

    if created:

        name, _ = instance.email.split("@")

        subject = "Your mail has been found to be use"
        body =  f"Hi {name.replace('.', ' ')},\nWe found the email '{instance.email}' being used on " + \
                "AtMailWin website for email automation. If this wasn't done by you, we strongly suggest you change your email's password and " + \
                "report to us on this <a href='https://github.com/PaulleDemon/Email-automation/issues'>page</a>. You can ignore this email if this was done by you."+\
                "\n\nBest regards,\nAtMailWin Team"
        
        send_html_mail_celery.delay(subject, message=body, html_message=body, recipient_list=[instance.email])
        