from datetime import datetime
import secrets
from threading import Lock
from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)
lock = Lock()

posts = {}


def generate_secured_key():
    """Generate a random, unique key for a post"""
    keys = [posts[p]['key'] for p in posts]
    while True:
        key = secrets.token_hex(16)
        if key not in keys:
            return key


def create_post(msg):
    """Create a new post with the given message"""
    with lock:
        post_id = len(posts) + 1000
        timestamp = datetime.utcnow().isoformat()
        post = {
            'id': post_id,
            'key': generate_secured_key(),
            'timestamp': timestamp,
            'msg': msg
        }
        posts[post_id] = post
        return post


def get_post_by_key(key):
    """Get the post with the given key"""
    with lock:
        for k, v in posts:
            if v['key'] == key:
                post = posts[v['id']]
                return jsonify({'id': post['id'], 'timestamp': post['timestamp'], 'msg': post['msg']}), 200


def get_post(post_id):
    """Get the post with the given ID"""
    with lock:
        if post_id not in posts:
            error = {'err': 'Post not found'}
            return jsonify(error), 404
        else:
            post = posts[post_id]
            return jsonify({'id': post['id'], 'timestamp': post['timestamp'], 'msg': post['msg']}), 200


def delete_post(post_id, key):
    """Delete the post with the given ID and key"""
    with lock:
        if post_id not in posts:
            error = {'err': 'Post not found'}
            return jsonify(error), 404
        else:
            post = posts[post_id]
            if key != post['key']:
                error = {'err': 'Forbidden'}
                return jsonify(error), 403
            else:
                curr_post = posts[post_id]
                del posts[post_id]
                return jsonify(curr_post), 200


@app.route('/', methods=['GET'])
def server_test():
    return 'Server is up and running on localhost:5000', 200


@app.route('/all-posts', methods=['GET'])
def get_all_posts():
    return posts, 200


@app.route('/post', methods=['POST'])
def handle_create_post():
    """Handle a POST request to create a new post"""
    if request.is_json:
        msg = request.json.get('msg')
        if msg is not None:
            post = create_post(msg)
            return jsonify(post), 200
    error = {'err': 'Bad request'}
    return jsonify(error), 400


@app.route('/post/<int:post_id>', methods=['GET'])
def handle_get_post(post_id):
    """Handle a GET request to get a post by ID"""
    return get_post(post_id)


@app.route('/post/<int:post_id>/delete/<string:key>', methods=['DELETE'])
def handle_delete_post(post_id, key):
    """Handle a DELETE request to delete a post by ID and key"""
    return delete_post(post_id, key)
