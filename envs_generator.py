import argparse
import secrets
import string
import os


# Generate a random password of length len
# if must_be_alphanumeric is TRUE then password will be alphanumeric,
# otherwise it will be alphabetical
def generate_password(len, must_be_alphanumeric):
    choices = string.ascii_letters
    if must_be_alphanumeric:
        choices += string.digits
    return ''.join(secrets.choice(choices) for i in range(len))


# generate .django file in .envs/.production directory
def generate_django_env_file_prod(hostname):
    django_file = "# General\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "# DJANGO_READ_DOT_ENV_FILE=True\n"
    django_file += "DJANGO_SETTINGS_MODULE=config.settings.production\n"
    django_file += "DJANGO_SECRET_KEY="
    django_file += generate_password(64, True) + "\n"
    django_file += "DJANGO_ADMIN_URL="
    django_file += generate_password(32, True) + "/\n"
    django_file += "DJANGO_ALLOWED_HOSTS="
    django_file += hostname + "\n\n"
    django_file += "# Security\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "# TIP: better off using DNS, however, redirect is OK too\n"
    django_file += "DJANGO_SECURE_SSL_REDIRECT=False\n\n"
    django_file += "# Email\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "MAILGUN_API_KEY=\n"
    django_file += "DJANGO_SERVER_EMAIL=\n"
    django_file += "MAILGUN_DOMAIN=\n\n"
    django_file += "# AWS\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "DJANGO_AWS_ACCESS_KEY_ID=\n"
    django_file += "DJANGO_AWS_SECRET_ACCESS_KEY=\n"
    django_file += "DJANGO_AWS_STORAGE_BUCKET_NAME=\n\n"
    django_file += "# django-allauth\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "DJANGO_ACCOUNT_ALLOW_REGISTRATION=True\n\n"
    django_file += "# Gunicorn\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "WEB_CONCURRENCY=4\n\n"
    django_file += "# Redis\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "REDIS_URL=redis://redis:6379/0\n\n"
    django_file += "# Celery\n"
    django_file += "# ---------------------------------------------------------------------------\n\n"
    django_file += "# Flower\n"
    django_file += "CELERY_FLOWER_USER="
    django_file += generate_password(32, True) + "\n"
    django_file += "CELERY_FLOWER_PASSWORD="
    django_file += generate_password(64, True) + "\n"
    os.makedirs(".envs/.production", exist_ok=True)
    f = open(".envs/.production/.django", "w")
    f.write(django_file)
    f.close()


# generate .postgres file in .envs/.production directory
def generate_postgres_env_file_prod():
    postgres_file = "# PostgreSQL\n"
    postgres_file += "# -------------------------------------------------------------------------\n"
    postgres_file += "POSTGRES_HOST=postgres\n"
    postgres_file += "POSTGRES_PORT=5432\n"
    postgres_file += "POSTGRES_DB=shakespeare_census\n"
    postgres_file += "POSTGRES_USER="
    postgres_file += generate_password(32, False) + "\n"
    postgres_file += "POSTGRES_PASSWORD="
    postgres_file += generate_password(64, True) + "\n"
    f = open(".envs/.production/.postgres", "w")
    f.write(postgres_file)
    f.close()
    return


# generate .django file in .envs/.local directory
def generate_django_env_file_loc():
    django_file = "# General\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "USE_DOCKER=yes\n\n"
    django_file += "# Redis\n"
    django_file += "# ---------------------------------------------------------------------------\n"
    django_file += "REDIS_URL=redis://redis:6379/0\n\n"
    django_file += "# Celery\n"
    django_file += "# ---------------------------------------------------------------------------\n\n"
    django_file += "# Flower\n"
    django_file += "CELERY_FLOWER_USER="
    django_file += generate_password(32, True) + "\n"
    django_file += "CELERY_FLOWER_PASSWORD="
    django_file += generate_password(64, True) + "\n"
    os.makedirs(".envs/.local", exist_ok=True)
    f = open(".envs/.local/.django", "w")
    f.write(django_file)
    f.close()


# generate .postgres file in .envs/.local directory
def generate_postgres_env_file_loc():
    postgres_file = "# PostgreSQL\n"
    postgres_file += "# -------------------------------------------------------------------------\n"
    postgres_file += "POSTGRES_HOST=postgres\n"
    postgres_file += "POSTGRES_PORT=5432\n"
    postgres_file += "POSTGRES_DB=shakespeare_census\n"
    postgres_file += "POSTGRES_USER="
    postgres_file += generate_password(32, False) + "\n"
    postgres_file += "POSTGRES_PASSWORD="
    postgres_file += generate_password(64, True) + "\n"
    f = open(".envs/.local/.postgres", "w")
    f.write(postgres_file)
    f.close()
    return


# generate .caddy file in .envs/.production directory
def generate_caddy_env_file():
    postgres_file = "# Caddy\n"
    postgres_file += "# -------------------------------------------------------------------------\n"
    postgres_file += "DOMAIN_NAME=example.com\n"
    f = open(".envs/.production/.caddy", "w")
    f.write(postgres_file)
    f.close()
    return


# return line with only leading whitespaces
def whitespace_template(line):
    num_leading_spaces = len(line) - len(line.lstrip(" "))
    line = ""
    for i in range(0, num_leading_spaces):
        line += " "
    return line


# generate new traefik.toml with updated hostname and voyant_hostname
def get_new_traefik_toml(lines, hostname, voyant_hostname):
    new_traefik_toml = ""
    rules_left = 3
    for line in lines:
        copy = line.strip()
        if copy.startswith("main"):
            line = whitespace_template(line)
            line += "main = \""
            line += hostname
            line += "\"\n"
        elif copy.startswith("sans"):
            line = whitespace_template(line)
            line += "sans = [\""
            line += voyant_hostname
            line += "\"]\n"
        elif copy.startswith("rule"):
            line = whitespace_template(line)
            line += "rule = \"Host:"
            if rules_left == 3:
                line += voyant_hostname
                line += "\"\n"
            elif rules_left == 2:
                line += voyant_hostname
                line += ";PathPrefix:/corpora\"\n"
            else:
                line += hostname
                line += "\"\n"
            rules_left -= 1
        new_traefik_toml += line
    return new_traefik_toml


# update hosts in traefik.toml
def update_traefik_toml(hostname, voyant_hostname, traefik_toml_path):
    f = open(traefik_toml_path)
    lines = f.readlines()
    f.close()
    new_traefik_toml = get_new_traefik_toml(lines, hostname, voyant_hostname)
    f = open(traefik_toml_path, "w")
    f.write(new_traefik_toml)
    f.close()
    return


# generate new voyant_gen.py with upated voyant_hostname
def get_new_voyant_gen_code(lines, voyant_hostname):
    new_python_code = ""
    for line in lines:
        copy = line.strip()
        if copy.startswith("url_template"):
            line = whitespace_template(line)
            line += "url_template = \'https://"
            line += voyant_hostname
            line += "/?input=https://"
            line += voyant_hostname
            line += "/corpora/{}\'\n"
        new_python_code += line
    return new_python_code


# update voyant-host in voyant_gen.py
def update_voyant_gen(voyant_hostname, voyant_gen_py_path):
    f = open(voyant_gen_py_path)
    lines = f.readlines()
    f.close()
    new_python_code = get_new_voyant_gen_code(lines, voyant_hostname)
    f = open(voyant_gen_py_path, "w")
    f.write(new_python_code)
    f.close()
    return


# get hostname from command-line
# get voyant_hostname (inferred from hostname)
def get_hostname():
    parser = argparse.ArgumentParser(
        description="Generate environment files for django and postgre")
    parser.add_argument("hostname")
    args = parser.parse_args()
    hostname = vars(args)["hostname"]
    return hostname


def main():
    # voyant_gen_py_path = "voyant_gen/voyant_gen.py"
    # traefik_toml_path = "compose/traefik/traefik.toml"
    hostname = get_hostname()
    # update_voyant_gen(voyant_hostname, voyant_gen_py_path)
    # update_traefik_toml(hostname, voyant_hostname, traefik_toml_path)
    generate_django_env_file_prod(hostname)
    generate_postgres_env_file_prod()
    generate_django_env_file_loc()
    generate_postgres_env_file_loc()
    generate_caddy_env_file()


if __name__ == "__main__":
    main()
