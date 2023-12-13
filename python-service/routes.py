import os
import logging
import flask
from flask import request, jsonify
from flask import json
from flask_cors import CORS
from dapr.clients import DaprClient

logging.basicConfig(level=logging.INFO)

app = flask.Flask(__name__)
CORS(app)

@app.route('/task', methods=['GET'])
def gettask():
    app.logger.info('task service called')
    with DaprClient() as d:
        d.wait(5)
        try:
            id = request.args.get('id')
            if id:
                # Get the task status from database via Dapr
                state = d.get_state(store_name='tasks', key=id)
                if state.data:
                    response = jsonify(json.loads(state.data))
                else:
                    response = jsonify('no task with that id found')
                response.status_code = 200
                return response
            else:
                response = jsonify('task "id" not found in query string')
                response.status_code = 500
                return response
        except Exception as e:
            app.logger.info(e)
            return str(e)
        finally:
            app.logger.info('completed task call')

@app.route('/task', methods=['POST'])
def createtask():
    app.logger.info('create task called')
    with DaprClient() as d:
        d.wait(5)
        try:
            # Get ID from the request body
            id = request.json['id']
            if id:
                # Save the task to database via Dapr
                d.save_state(store_name='tasks', key=id, value=json.dumps(request.json))
                response = jsonify(request.json)
                response.status_code = 200
                return response
            else:
                response = jsonify('task "id" not found in query string')
                response.status_code = 500
                return response
        except Exception as e:
            app.logger.info(e)
            return str(e)
        finally:
            app.logger.info('created task')

@app.route('/task', methods=['DELETE'])
def deletetask():
    app.logger.info('delete called in the task service')
    with DaprClient() as d:
        d.wait(5)
        id = request.args.get('id')
        if id:
            # Delete the task status from database via Dapr
            try: 
                d.delete_state(store_name='tasks', key=id)
                return f'Item {id} successfully deleted', 200
            except Exception as e:
                app.logger.info(e)
                return abort(500)
            finally:
                app.logger.info('completed task delete')
        else:
            response = jsonify('task "id" not found in query string')
            response.status_code = 400
            return response

app.run(host='0.0.0.0', port=os.getenv('PORT', '5000'))