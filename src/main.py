from flask import (
    Flask,
    url_for,
    abort,
    render_template,
    redirect,
    request,
    jsonify,
    g
)
from database import (
    close_db,
    get_k8s_contexts,
    get_all_versions_for_application,
    get_latest_versions_for_context,
    add_context,
    add_version,
    add_application
)
from k8s import (
    get_kubernetes_workloads
)
from markupsafe import escape
from pprint import pprint
import os


def create_app():
    """
    create the flask app object
    """
    app = Flask(
        __name__, 
        template_folder='../templates',
        static_folder='../static'
        )
    app.config.from_mapping(
        MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE'),
        MYSQL_HOST = os.environ.get('MYSQL_HOST'),
        MYSQL_USER = os.environ.get('MYSQL_USER'),
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD'),
        MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
    )
    app.teardown_appcontext(close_db)
    return app


app = create_app()


@app.route('/', defaults={'context': ''})
@app.route('/<context>')
def index(context):
    """
    the kubernetes versions for the given kubernetes context parameter are looked up in the database and shown in a table
    """
    contexts = get_k8s_contexts()

    if context in contexts:
        version_history = get_latest_versions_for_context(context)

        return render_template('index.html', selected_context=context, contexts=contexts, version_history=version_history)
        
    if not context:
        return render_template("error.html", error=f"select a kubernetes context from the menu", contexts=contexts)


    return render_template("error.html", error=f"no k8s context with name '{escape(context)}' could be found", contexts=contexts)


@app.route("/<context>/<application>")
def show(context, application):
    """
    Show the complete version history for an application and the corresponding context
    """
    versions = get_all_versions_for_application(application, context)
    return render_template('show.html', versions=versions, selected_context=context)


@app.route("/update-version-history/<context>")
def update_version_history(context):
    """
    update all version numbers of all components that can be found in the given kubernetes context
    """
    if request.method == "GET":

        k8s_workloads = get_kubernetes_workloads(context)

        if k8s_workloads is None:
            abort(500, "An error occured")

        add_context(escape(context))

        for workload_type in k8s_workloads:
            for item in workload_type.items:
                try:
                    image = item.spec.template.spec.containers[0].image
                    splitImage = image.split(":")
                    if (len(splitImage) > 1):
                        version = splitImage[1]
                        application = splitImage[0].split("/")[-1]
                        # pprint(f"application: {application} version: {version}")

                        if version and application:
                            add_application(escape(application))
                            add_version(escape(version), context, application)

                except AttributeError as e:
                    abort(500, "An error occured when trying to fetch the the version number of a workload: {e}")

        return "OK"


@app.route("/health")
def health():
    return "OK"


if __name__ == '__main__':
    app.run()