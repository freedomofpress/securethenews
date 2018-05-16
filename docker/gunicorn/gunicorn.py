import os

raw_env = ["{}={}".format(x, os.environ[x])
           for x in os.environ.keys()
           if x.startswith('DJANGO')]
print(raw_env)
user = "gcorn"
group = "gcorn"
bind = ['0.0.0.0:8000']
loglevel = "debug"
capture_output = False
