import django, os, logging, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
logging.getLogger('django').warning('test logstash connection')
time.sleep(2)
print('Done')
