# k8s-version-dashboard

This simple flask app uses the python kubernetes client library to fetch all kubernetes workloads from a cluster and store it in a MySQL database.

## create virtual environment for python dependencies
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
You should now see a prefix `(venv)` in your command line. To leave the virtual environment just type `deactivate`.

## required environment variables

```
export MYSQL_HOST=localhost
export MYSQL_DATABASE=k8s_version_dashboard
export MYSQL_USER=user
export MYSQL_PASSWORD=password
export MYSQL_PORT=3306
```

## Import mysql schema manually

You can import the sql schema located under `sql_schema` via `mysql -h hostname < sql_schema/schema.sql`

## CSS Template

This project is based on the css template bulma.io: https://github.com/jgthms/bulma

## Updating the version history

The version history can be updated by calling the endpoint /update-version-history/<k8s_context>. A kubernetes Cron can be used to update the history frequently. 