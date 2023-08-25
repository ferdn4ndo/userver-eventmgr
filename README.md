# uServer FileMgr

File management microservice based on django-rest-framework with AWS S3 integration

It's part of the [uServer](https://github.com/users/ferdn4ndo/projects/1) stack project.

## Using It

### Prepare the environment

Copy `.env.template` to `.env` and edit it accordingly.

### Run the Application

```sh
docker-compose up --build
```

### Setup it (first run only)

Take a look at `setup.sh` and adjust it accordingly if needed, then run:

```sh
docker exec -it userver-filemgr sh -c "./setup.sh"
```

Access the application at the address [http://localhost:5000/](http://localhost:5000/) or any other environment configuration you made.

## Documentation

The API schema is provided in two formats:

* with a GET at `<host>/docs/openapi/`, which will retrieve the [OpenAPI](https://swagger.io/specification/) YAML specification file with all the endpoints;

* with a GET at `<host>/docs/redoc/`, which will retrieve the [ReDoc](https://github.com/Redocly/redoc) API Reference Documentation for userver-filemgr, in an interactive interface;


### Endpoints Summary

#### `/media-images/` Namespace

* **GET** `/media-images/`: List images;
* **GET** `/media-images/<media-image-id>/`: Show image metadata and available sizes;
* **POST** `/media-images/<media-image-id>/download/`: Download the biggest size tag;
* **POST** `/media-images/<media-image-id>/download/<size-tag>/`: Download a specific size tag;

#### `/storages/` Namespace

* **GET** `/storages/`: List storages;
* **POST** `/storages/`: Create a new storage;
* **GET** `/storages/<storage-id>/`: Read a storage;
* **PATCH** `/storages/<storage-id>/`: Update a storage;
* **DELETE** `/storages/<storage-id>/`: Delete a storage;
* **GET** `/storages/<storage-id>/files/`: List the storage files;
* **GET** `/storages/<storage-id>/files/<file-id>/`: Read a file info;
* **PATCH** `/storages/<storage-id>/files/<file-id>/`: Update (metadata only) a file;
* **DELETE** `/storages/<storage-id>/files/<file-id>/`: Delete a file (move to trash);
* **POST** `/storages/<storage-id>/files/<file-id>/download/`: Download the raw storage file;
* **POST** `/storages/<storage-id>/upload-from-url`: Upload a new file to the storage from a URL;
* **POST** `/storages/<storage-id>/upload-from-file`: Upload a new file to the storage from a local one;
* **GET** `/storages/<storage-id>/trash/`: List the files in the recycled bin;
* **GET** `/storages/<storage-id>/trash/<file-id>/`: Read a file in the recycled bin/Permanently delete the file;
* **DELETE** `/storages/<storage-id>/trash/<file-id>/`: Permanently delete the file;

## Testing

### Without coverage:

```sh
docker exec -it userver-filemgr sh -c "python manage.py test filemgr"
```

### With coverage:

```sh
docker exec -it userver-filemgr sh -c "python manage.py cov filemgr"
```

## Utils

General commands for userver-filemgr. Most of them are based on [django-extensions](https://github.com/django-extensions/django-extensions).

### Create DB models chart

Generate (and view) a graphviz graph of app models:

```
docker exec -it userver-filemgr sh -c "python manage.py graph_models -a -o filemgr_models.png"
```

### Generate list of URLs

Produce a tab-separated list of (url_pattern, view_function, name) tuples for a project:

```
docker exec -it userver-filemgr sh -c "python manage.py show_urls"
```

### Check templates

Check templates for rendering errors:

```
docker exec -it userver-filemgr sh -c "python manage.py validate_templates"
```

### Enhanced Django shell

Run the enhanced django shell:

```
docker exec -it userver-filemgr sh -c "python manage.py shell_plus"
```


### Updating OpenAPI schema

To update the OpenAPI schema:

```sh
docker exec -it userver-filemgr sh -c "python manage.py generateschema" > openapi-schema.yaml
```
