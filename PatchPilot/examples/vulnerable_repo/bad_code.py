import subprocess
import yaml
import os

def run_command(user_input):
    subprocess.call(["ping", user_input], shell=False)


def load_config(file_path):
    with open(file_path) as f:
        return yaml.load(f)


AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


def run_query(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return query