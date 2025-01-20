# Foxbit-API
An API for buying and selling cryptocurrencies

## Migrations

```sh
python3 app/add_migration.py
```

## Heroku

```sh
heroku logs --tail --app {app-name}
heroku run python -m app.scripts --environment=production --app {app-name}
heroku pg:psql --app {app-name}
```
