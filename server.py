from flask import Flask, jsonify, request
import flask
from flask_cors import CORS
from stitch_tiles import stitch_tiles
from sse import Publisher

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
publisher = Publisher()


@app.route('/subscribe')
def subscribe():
    return flask.Response(publisher.subscribe(),
                          content_type='text/event-stream')


@app.route('/', methods=['GET', 'OPTIONS'])
def running():
    return 'Server is running'


@app.route('/process_tiles', methods=['GET', 'POST', 'OPTIONS'])
def process_tiles():  # put application's code here
    if request.is_json:
        request_data = request.get_json()
        bbox = request_data['bbox']
        zoom = request_data['zoom']
        filename = request_data['filename']
        access_token = request_data['access_token']
        api_url = request_data['api_url']
        base_dir = request_data['base_dir']
        composite_dir = request_data['composite_dir']
        stitch_tiles(bbox, zoom, filename, access_token, api_url, base_dir, composite_dir, publisher)
        print('done stitching')
        return {'msg': 'done'}
    else:
        return jsonify({'error': 'not json'})


if __name__ == '__main__':
    app.run()

# app.run(debug=True, threaded=True)
