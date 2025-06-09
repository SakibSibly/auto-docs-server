# auto-docs-server
Back-end for automatic document generation system.

## Requirements

Run the `requirements.txt` to install the dependencies.

```sh
pip install -r requirements.txt
```

## Enviroment variables generation

Run `generate_env_file.py` from the `scripts` directory.

```sh
python ./scripts/generate_env_file.py
```

- Edit the files of database configurations if you're in the production environment.
- For local development set `DJANGO_ENV=local` and can leave the database configurtions unchanged.

## Run the development server

Apply migrations to the database.

```sh
python manage.py makemigrations
python manage.py migrate
```

Run `manage.py` from the directory.

```sh
python manage.py runserver
```


test1