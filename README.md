# k8s-version-dashboard

This simple flask app uses the python kubernetes client library to fetch all kubernetes workloads from a cluster, stores them in a MySQL database
and visualizes them.

## create virtual environment for python dependencies
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
You should now see a prefix `(venv)` in your command line. To leave the virtual environment just type `deactivate`.

## required environment variables

You can use `python-dotenv` to inject all environment variables automatically from a file. Simply add the following variables in a `.env`-file inside the root folder and change their respective value.
```
MYSQL_HOST=localhost
MYSQL_DATABASE=k8s_version_dashboard
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_PORT=3306
# when using mysql as docker container
MYSQL_ROOT_PASSWORD=example
```

## Import mysql schema manually

You can import the sql schema located under `sql_schema` via `mysql -h hostname < sql_schema/schema.sql`

## Add cluster credentials to the Dockerfile (GCP)

To add cluster credentials to the Dockerfile you will need to adapt the following command lines:
```
# The example here is for Google Cloud Platform / GKE: 
RUN gcloud container clusters get-credentials <cluster name> --zone <zone> --project <project>
RUN kubectl config rename-context <old context> <new context>
```
The docker file expects a service account key file `credentials.json` in the same path to authenticate to the cluster(s). 

For other cloud platforms, the Dockerfile would have to be adapted accordingly.

## Build and run the container using podman

You can build and run the docker either with docker or podman. 
Make sure the `.env` file containing the environment variables from above is located in the project folder.
```
podman build -t k8s-version-dashboard .
podman run -d -p 5000:5000 --env-file=.env k8s-version-dashboard
```
It is also possible to quickly start the app including a mysql database using podman-compose. This will also read in the mysql schema automatically. Make sure the folder `./sql_data` exists in the project directory before running:
```
podman-compose up
```

## Updating the version history

The version history can be updated by calling the endpoint `/update-version-history/<k8s_context>`. A (kubernetes) cron job can be used to update the history frequently. 