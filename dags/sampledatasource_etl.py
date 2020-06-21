"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.kubernetes.pod import Port
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator

port = Port('http', 80)

env_vars = {
    "KUBERNETES_SERVICE_HOST": "10.0.0.1",
    "KUBERNETES_SERVICE_PORT": "443",
    "KUBERNETES_SERVICE_PORT_HTTPS": "443"
}

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2020, 6, 20),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(
    "sampledatasource_etl",
    default_args=default_args,
    schedule_interval=timedelta(minutes=5),
    concurrency=1,
    max_active_runs=1
)

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(task_id="print_date", bash_command="date", dag=dag)

# t2 = BashOperator(task_id="sleep", bash_command="sleep 5", retries=3, dag=dag)

# templated_command = """
#     {% for i in range(5) %}
#         echo "{{ ds }}"
#         echo "{{ macros.ds_add(ds, 7)}}"
#         echo "{{ params.my_param }}"
#     {% endfor %}
# """
#
# t3 = BashOperator(
#     task_id="templated",
#     bash_command=templated_command,
#     params={"my_param": "Parameter I passed in"},
#     dag=dag,
# )

# t4 = DockerOperator(
#     task_id="docker_run",
#     image="mavx/sampledatasource_etl:latest",
#     api_version="auto",
#     auto_remove=True,
#     command=["python", "etl.py"],
#     network_mode="host",
#     tty=True,
#     docker_conn_id="dockerhub",
#     dag=dag,
# )
#
# t5 = DockerOperator(
#     task_id="docker_run_echo",
#     image="python:3.7-slim",
#     api_version="auto",
#     auto_remove=True,
#     command=["echo", "1"],
#     network_mode="host",
#     tty=True,
#     docker_conn_id="dockerhub",
#     dag=dag,
# )

t6 = KubernetesPodOperator(
    task_id="k8s_run",
    in_cluster=False,
    namespace="default",
    image="mavx/sampledatasource_etl:latest",
    cmds=["python", "etl.py"],
    name="k8s_task_pod",
    cluster_context="docker-desktop",
    is_delete_operator_pod=True,
    ports=[port],
    dag=dag,
)

# t5 = BashOperator(
#     task_id="docker_run_echo",
#     bash_command="docker ps",
#     # params={"my_param": "Parameter I passed in"},
#     dag=dag,
# )

# t2.set_upstream(t1)
# t3.set_upstream(t1)
# t4.set_upstream(t3)
# t5.set_upstream(t3)

t1 >> t6

if __name__ == '__main__':
    t6.execute("ds")
