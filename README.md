# k8s-version-dashboard

This simple flask app uses the python kubernetes client library to fetch all kubernetes workloads from a cluster and store it in a MySQL database.

## create virtual environment for python dependencies
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
You should now see a prefix `(venv)` in your command line. To leave the virtual environment just type `deactivate`.

## Import mysql schema manually

You can import the sql schema located under `sql_schema` via `mysql -h hostname < sql_schema/schema.sql`

## required environment variables

```
export MYSQL_HOST=localhost
export MYSQL_DATABASE=k8s_version_dashboard
export MYSQL_USER=user
export MYSQL_PASSWORD=password
export MYSQL_PORT=3306
```

## Add cluster credentials to the Dockerfile (GCP)

To add cluster credentials to the Dockerfile you will need to adapt the following command lines in Dockerfile:
```
# The example here is for Google Cloud Platform / GKE: 
RUN gcloud container clusters get-credentials <cluster name> --zone <zone> --project <project>
RUN kubectl config rename-context <old context> <new context>
```
The docker file expects a service account key file `credentials.json` in the same path to authenticate to the cluster(s). 

For other cloud platforms, the Dockerfile would have to be adapted accordingly.

## Updating the version history

The version history can be updated by calling the endpoint /update-version-history/<k8s_context>. A kubernetes Cron can be used to update the history frequently. 