# This is a very sloppy way of getting backups out of the docker container.
# Run it, copy the output, and paste it back into the terminal.

echo "sudo docker-compose -f production.yml run --rm django python manage.py exportjson $1"
echo "sudo docker-compose -f production.yml run --rm django python manage.py exportjson latest"
sudo docker exec -it shakespearecensusproduction_django_run_1 /entrypoint find . -maxdepth 1 -iname *_*.json | \
    grep .*_.*.json | \
    sed "s/\./sudo docker cp shakespearecensusproduction_django_run_1:app/" | \
    sed "s/\.json/.json . /"
