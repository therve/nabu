"""
Example script for getting events over a Zaqar queue.

To run:
$ export IDENTITY_API_VERSION=3
$ source ~/devstack/openrc
$ python example.py
"""
import json
import os
import uuid

import requests
import websocket

from keystoneauth1.identity import v3
from keystoneauth1 import session


client_id = str(uuid.uuid4())


def authenticate(ws, token, project_id):
    ws.send(json.dumps(
        {'action': 'authenticate',
         'headers': {'X-Auth-Token': token,
                     'Client-ID': client_id,
                     'X-Project-ID': project_id}}))
    return ws.recv()


def send_message(ws, project_id, action, body=None):
    msg = {'action': action,
           'headers': {'Client-ID': client_id, 'X-Project-ID': project_id}}
    if body:
        msg['body'] = body
    ws.send(json.dumps(msg))
    return json.loads(ws.recv())


def main():
    auth_url = os.environ.get('OS_AUTH_URL')
    user = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    project = os.environ.get('OS_PROJECT_NAME')
    auth = v3.Password(auth_url=auth_url,
                       username=user,
                       user_domain_name='default',
                       password=password,
                       project_name=project,
                       project_domain_name='default')
    sess = session.Session(auth=auth)
    token = auth.get_token(sess)
    project_id = auth.get_project_id(project)

    nabu_url = auth.get_endpoint(sess, service_type='subscription')
    requests.post('%s/v1/subscription' % (nabu_url,),
                  data=json.dumps({'source': 'compute',
                                   'target': 'nabu_queue'}),
                  headers={'X-Auth-Token': token,
                           'Content-Type': 'application/json'})
    ws_url = auth.get_endpoint(sess, service_type='messaging-websocket')
    ws = websocket.create_connection(ws_url.replace('http', 'ws'))
    authenticate(ws, token, project_id)
    send_message(ws, project_id, 'queue_create', {'queue_name': 'nabu_queue'})
    send_message(ws, project_id, 'subscription_create',
                 {'queue_name': 'nabu_queue', 'ttl': 3000})
    while True:
        ws.recv()


if __name__ == '__main__':
    main()
