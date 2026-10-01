import subprocess
import yaml

def run_command(user_input):
    subprocess.call("ping " + user_input, shell=True)


def load_config(file_path):
    with open(file_path) as f:
        return yaml.load(f)


AWS_SECRET_ACCESS_KEY = "AKIAABCDEFGHIJKLMNOP"


def run_query(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return query
