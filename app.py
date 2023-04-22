import http
import secrets
from datetime import datetime
from threading import Lock
import uuid
from flask import Flask, jsonify, request
from http import HTTPStatus
app = Flask(__name__)
lock_request = Lock()

posts = {}
n_bytes = 16


def generate_secured_key():
    """Generate a random, unique key for a post"""
    keys = [posts[p]['key'] for p in posts]
    while 1 == 1:
        key = secrets.token_hex(n_bytes)
        if key not in keys:
            return key


def create_post(msg):
    """Create a new post with the given message"""
    with lock_request:
        curr_post_id = len(posts) + 1000
        timestamp = datetime.utcnow().isoformat()
        curr_post = {
            'id': curr_post_id,
            'key': generate_secured_key(),
            'timestamp': timestamp,
            'msg': msg
        }
        posts[curr_post_id] = curr_post
        return curr_post


def get_post_by_key(key):
    """Get the post with the given key"""
    with lock_request:
        for k, v in posts:
            if v['key'] == key:
                post = posts[v['id']]
                return jsonify({'id': post['id'], 'timestamp': post['timestamp'], 'msg': post['msg']}), HTTPStatus.OK.value


def get_post(post_id):
    """Get the post with the given ID"""
    with lock_request:
        if post_id not in posts:
            error = {'err': f'The post is not found with id: {post_id}'}
            return jsonify(error), HTTPStatus.NOT_FOUND.value
        else:
            post = posts[post_id]
            post_response = {'id': post['id'], 'timestamp': post['timestamp'], 'msg': post['msg']}
            return jsonify(post_response), HTTPStatus.OK.value


def delete_post(post_id, key):
    """Delete the post with the given ID and key"""
    with lock_request:
        if post_id not in posts:
            error = {'err': f'The post is not found with id: {post_id}'}
            return jsonify(error), HTTPStatus.NOT_FOUND.value
        else:
            post = posts[post_id]
            if key != post['key']:
                error = {'err': f'The request has been forbidden for key: {key}'}
                return jsonify(error), HTTPStatus.FORBIDDEN.value
            else:
                curr_post = posts[post_id]
                del posts[post_id]
                return jsonify(curr_post), HTTPStatus.OK.value


@app.route('/', methods=['GET'])
def server_test():
    return 'Server is up and running on localhost:5000', HTTPStatus.OK.value


@app.route('/all-posts', methods=['GET'])
def get_all_posts():
    return posts, HTTPStatus.OK.value


@app.route('/post', methods=['POST'])
def handle_create_post():
    """Handle a POST request to create a new post"""
    if request.is_json:
        msg = request.json.get('msg')
        if msg is not None:
            post = create_post(msg)
            return jsonify(post), HTTPStatus.OK.value
    error = {'err': 'Bad request'}
    return jsonify(error), HTTPStatus.BAD_REQUEST.value


@app.route('/post/<int:post_id>', methods=['GET'])
def handle_get_post(post_id):
    """Handle a GET request to get a post by ID"""
    return get_post(post_id)


@app.route('/post/<int:post_id>/delete/<string:key>', methods=['DELETE'])
def handle_delete_post(post_id, key):
    """Handle a DELETE request to delete a post by ID and key"""
    return delete_post(post_id, key)
