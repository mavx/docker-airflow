#!/bin/bash

export AIRFLOW_HOME=.

airflow initdb
sleep 10
airflow webserver -p 8080 &
sleep 10
airflow scheduler &
sleep 10
