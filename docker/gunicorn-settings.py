# Settings for gunicorn in docker.
import multiprocessing


bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog =  "/log/access.log"
worker_tmp_dir = "/dev/shm"
