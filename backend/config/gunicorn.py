# The socket to bind.
bind = "0.0.0.0:8000"

# The number of worker processes for handling requests.
workers = 4  # A good starting point is (2 x $num_cores) + 1

# The maximum number of simultaneous clients.
# worker_connections = 1000

# The maximum number of requests a worker will process before restarting.
# max_requests = 1000

# The number of seconds to wait for requests on a Keep-Alive connection.
timeout = 120

# The path to the log files.
# Make sure the directory exists. We already mounted it in docker-compose.
accesslog = "/var/log/django/gunicorn.access.log"
errorlog = "/var/log/django/gunicorn.error.log"

# Whether to send Django output to the error log.
capture_output = True

# The granularity of error log output.
loglevel = "info"
