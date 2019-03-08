# This is a very sloppy way of getting backups out of the docker container.
# Run it, copy the output, and paste it back into the terminal.

echo "sudo docker exec -it shakespearecensusproduction_django_1 /entrypoint python manage.py exportjson $1"
echo "sudo docker exec -it shakespearecensusproduction_django_1 /entrypoint python manage.py exportjson latest"
docker exec -it shakespearecensusproduction_django_1 /entrypoint find . -maxdepth 1 -iname *_*.json | \
    grep .*_.*.json | \
    sed "s/\./sudo docker cp shakespearecensusproduction_django_1:app/" | \
    sed "s/\.json/.json . /"
