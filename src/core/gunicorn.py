command = '/usr/src/venv/bin/gunicorn'
pythonpath = '/usr/src'
bind = '0.0.0.0:8000'
workers = 5
timeout = 120

# SSL configuration (commented out as nginx will handle SSL)
# certfile = '/usr/src/cert.crt'
# keyfile = '/usr/src/private.key'

# Access log - records incoming HTTP requests
accesslog = "/usr/src/logs/gunicorn.access.log"

# Error log - records gunicorn server goings-on
errorlog = "/usr/src/logs/gunicorn.error.log"

# Whether to send Django output to the error log
capture_output = True

# How verbose the Gunicorn error logs should be
loglevel = "info"
