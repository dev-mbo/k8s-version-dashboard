"""
module to operate on the database
"""
import sys
from pprint import pprint
import mariadb
from flask import current_app, g


def get_db():
    """
    initialize the database connection
    """
    host = current_app.config['MYSQL_HOST']
    port = current_app.config['MYSQL_PORT']
    user = current_app.config['MYSQL_USER']
    password = current_app.config['MYSQL_PASSWORD']
    database = current_app.config['MYSQL_DATABASE']

    if 'db' not in g:
        try:
            g.db = mariadb.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                autocommit=True
            )
        except mariadb.Error as error:
            current_app.logger.error(f"Error connecting to database: {error}")
            sys.exit(1)

    return g.db


def close_db(event=None):
    """
    close database connection, this function is called in the teardown context of the app
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def get_all_versions_for_application(application, context):
    """
    fetch all versions that have been logged for an application and the corresponding context
    """
    try:
        cur = get_db().cursor()
        cur.execute(
            """
            SELECT v.version_no as version,
                   v.created as created
            FROM version_history v
            INNER JOIN application a ON a.id = v.application_id
            INNER JOIN context c ON c.id = v.context_id
            WHERE a.name = ?
            AND c.name = ?
            ORDER BY created DESC
            """,
            (application, context)
        )
        versions = []
        for (version, created) in cur:
            versions.append({
                'version': version,
                'created': created
            })
        return versions
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def get_k8s_contexts():
    """
    fetch all available kubernetes context from the database
    """
    try:
        cur = get_db().cursor()
        cur.execute(
            """
                SELECT name as context_name
                FROM context
                ORDER BY name ASC
            """
        )
        contexts = []
        for [context_name] in cur:
            print(context_name)
            contexts.append(context_name)

        return contexts
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def get_latest_versions_for_context(context):
    """
    fetch the latest versions for a kubernetes context
    """
    try:
        cur = get_db().cursor()
        cur.execute(
            """
            SELECT v.version_no as version,
                   a.name as application
            FROM version_history v
            INNER JOIN application a ON a.id = v.application_id
            WHERE v.id IN (
                SELECT max(v2.id)
                FROM version_history v2
                INNER JOIN context c ON c.id = v2.context_id
                WHERE c.name = ?
                GROUP BY v2.application_id
            )
            ORDER BY application
            """,
            [context]
        )
        version_history = []
        for (version, application) in cur:
            version_history.append({
                'application': application,
                'version': version,
            })
        return version_history
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def add_context(context):
    """
    add a kubernetes context to context sql table
    """
    try:
        get_db().cursor().execute("INSERT IGNORE INTO context (name) VALUES (?)", [context])
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def add_application(application):
    """
    add a new application to the application sql table
    """
    try:
        get_db().cursor().execute("INSERT IGNORE INTO application (name) VALUES (?)", [application])
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def add_version(version, context, application):
    """
    add a new version to the version_history sql table
    """
    try:
        last_added_version = get_last_added_version(application, context)
        pprint(f"last_added_version: {application} {last_added_version} {version}")
        if last_added_version is None or last_added_version != version:
            get_db().cursor().execute(
                """
                    INSERT IGNORE INTO version_history (application_id, context_id, version_no)
                    VALUES(
                        (SELECT id from application WHERE name = ?),
                        (SELECT id from context where name = ?),
                        ?
                    )
                """,
                (application, context, version)
            )
            return True

        return False
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def get_last_added_version(application, context):
    """
    retrieve the last added version for an application in a cluster context, to test
    if the new version is the same as the previous one
    """
    try:
        cur = get_db().cursor()
        cur.execute(
            """
                SELECT v.version_no
                FROM version_history v
                INNER JOIN application a ON a.id = v.application_id
                INNER JOIN context c ON c.id = v.context_id
                WHERE a.name = ?
                AND c.name = ?
                ORDER BY created DESC LIMIT 1
            """,
            (application, context)
        )
        row = cur.fetchone()
        if row is not None:
            return row[0]

        return None
    except mariadb.Error as error:
        current_app.logger.error(f"Error: {error}")


def add_version_and_application(version, context, application):
    """
    add new row to version history
    """
    if version and context and application:
        add_application(application)
        return add_version(version, context, application)

    return False
