"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count
from os import environ
import gunicorn

def max_workers():    
    return cpu_count()

bind = '0.0.0.0:8080'
max_requests = 1000
worker_class = 'gevent'
workers = 2 # max_workers()
gunicorn.SERVER = 'undisclosed'
