from kubernetes import (
    client, 
    config, 
)
from kubernetes.client import (
    ApiException
)
from kubernetes.config import (
    ConfigException
)
from flask import (
    Flask, 
    current_app, 
    g
)


def get_kubernetes_workloads(context):
    try:
        config.load_kube_config(context=context)
        api = client.AppsV1Api()

        deployments = api.list_deployment_for_all_namespaces(watch=False)
        statefulsets = api.list_stateful_set_for_all_namespaces(watch=False)
        daemonsets = api.list_daemon_set_for_all_namespaces(watch=False)

        k8s_workloads = [ deployments, statefulsets, daemonsets ]

        return k8s_workloads
    except ApiException as e:
        current_app.logger.error(f"An error occured when fetching the workloads for context {context}: {e}")
    except ConfigException as e:
        current_app.logger.error(f"An error occured when loading the config for context {context}: {e}")