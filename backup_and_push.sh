# Move most recent data to archive.
mv -f census/ingest/data/json-backups/latest/* census/ingest/data/json-backups/dated/

# Make folder writable by anyone. This is the easiest way to work around
# the problem that the container's django user doesn't have write privileges.
chmod -R o+w census/ingest/data/json-backups/latest

# Run the backup routine in a disposable container.
sudo docker-compose -f production.yml run --rm django python3 manage.py exportjson census/ingest/data/json-backups/latest/`date +'%Y-%m-%d'`

# Files will be saved under the django user's UID, which locally translates
# to some weird system account. So change back to current user.
sudo chown -R $USER:$USER census/ingest/data/json-backups

# Make folder read-only again for all other users.
chmod -R o-w census/ingest/data/json-backups

# Commit and push changes to git.
git add census/ingest/data/json-backups
git commit -m "latest backup"
git push
