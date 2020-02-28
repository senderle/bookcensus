chmod -R o+w census/ingest/data/json-backups
sudo docker-compose -f production.yml run --rm django python3 manage.py exportjson census/ingest/data/json-backups/latest
sudo chown -R senderle:senderle census/ingest/data
chmod -R o-w census/ingest/data/json-backups
