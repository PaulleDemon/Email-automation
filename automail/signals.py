import json
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, post_delete

from django_celery_beat.models import PeriodicTask, ClockedSchedule, IntervalSchedule


from .models import EmailCampaignTemplate


@receiver(post_save, sender=EmailCampaignTemplate)
def schedule_email(instance, sender, created, *args, **kwargs):

    if instance.scheduled:
        schedule_start = ClockedSchedule.objects.create(clocked_time=instance.schedule)

        PeriodicTask.objects.create(name=f'email_{instance.id}', clocked=schedule_start, one_off=True, 
                                        kwargs=json.dumps({'id': instance.id}), 
                                        task='run_schedule_email')

@receiver(pre_delete, sender=EmailCampaignTemplate)
def remove_scheduled_mail(sender, instance, **kwargs):

    try: 
        task = PeriodicTask.objects.get(name=f'email_{instance.id}')
        task.enabled = False
        task.save()
        task.delete()

    except (PeriodicTask.DoesNotExist):
        pass
