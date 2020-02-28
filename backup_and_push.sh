mv -f census/ingest/data/json-backups/latest/* census/ingest/data/json-backups/dated/
chmod -R o+w census/ingest/data/json-backups
sudo docker-compose -f production.yml run --rm django python3 manage.py exportjson census/ingest/data/json-backups/latest/`date +'%Y-%m-%d'`
sudo chown -R senderle:senderle census/ingest/data
chmod -R o-w census/ingest/data/json-backups
git add census/ingest/data/json-backups/latest*
git commit -m "latest backup"
git push
