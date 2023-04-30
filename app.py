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
users = {}


def generate_secured_key():
    """Generate a random, unique key for a post"""
    keys = [posts[p]['key'] for p in posts]
    while 1 == 1:
        key = secrets.token_hex(n_bytes)
        if key not in keys:
            return key


def generate_secured_user_key():
    """Generate a random, unique key for a user"""
    while 1 == 1:
        key = secrets.token_hex(n_bytes)
        user_keys = [users[u]['key'] for u in users]
        if key not in user_keys:
            return key


def is_valid_user_key(user_id, user_key):
    curr_user = users[user_id]
    if curr_user is not None:
        return curr_user['key'] == user_key
    return False


def create_post(msg, user_id):
    """Create a new post with the given message"""
    with lock_request:
        curr_post_id = len(posts) + 1000
        curr_post = {
            'id': curr_post_id,
            'key': generate_secured_key(),
            'timestamp': datetime.utcnow().isoformat(),
            'msg': msg
        }

        if user_id is not None:
            curr_post['user_id'] = user_id
            # curr_post['user_key'] = user_key
        posts[curr_post_id] = curr_post
        return curr_post


def create_user(user_json):
    """
    Create a user from input json body
    metadata: unique user_id, name, phone_num, city
    user object: user_id, name, phone_num, city, created_at, user_key
    :param user_json: user json
    :return: newly created user
    """
    with lock_request:
        default_unique_user_key = generate_secured_user_key()
        curr_user = {
            'user_id': user_json.get('user_id'),
            'key': default_unique_user_key,
            'created_at': datetime.utcnow().isoformat()
        }
        if user_json.get('name') is not None:
            curr_user['name'] = user_json.get('name')
        if user_json.get('phone_num') is not None:
            curr_user['phone_num'] = user_json.get('phone_num')
        if user_json.get('city') is not None:
            curr_user['city'] = user_json.get('city')
        users[user_json.get('user_id')] = curr_user
        return curr_user


def update_user(user_json, user_id):
    with lock_request:
        curr_user = users.get(user_id)
        if user_json.get('name') is not None:
            curr_user['name'] = user_json.get('name')
        if user_json.get('phone_num') is not None:
            curr_user['phone_num'] = user_json.get('phone_num')
        if user_json.get('city') is not None:
            curr_user['city'] = user_json.get('city')
        users[user_id] = curr_user
        user_ret = curr_user.copy()
        del user_ret['key']
        return user_ret


# def generate_new_user_key(user_id):
#     with lock_request:
#         unique_user_key = generate_secured_user_key()
#         curr_user = users.get(user_id)
#         curr_user['key'] = unique_user_key
#         users[user_id] = curr_user
#         return curr_user


def get_user(user_id):
    with lock_request:
        curr_user = users[user_id].copy()
        del curr_user['key']
        return curr_user


def get_post_by_key(key):
    """Get the post with the given key"""
    with lock_request:
        for k, v in posts:
            if v['key'] == key:
                post = posts[v['id']]
                return jsonify(
                    {'id': post['id'], 'timestamp': post['timestamp'], 'msg': post['msg']}), HTTPStatus.OK.value


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


def is_valid_key(post_id, key):
    """
    Checks whether the current key is valid user or valid post key whatever it is.
    :param post_id: id of the post
    :param key: key passed as an input
    :return: boolean: true if key is valid
    """

    if post_id in posts:
        curr_post = posts[post_id]
        if curr_post.get('user_id') is not None:
            user_keys = [users[u]['key'] for u in users]
            user_id = curr_post.get('user_id')
            if key in user_keys:
                return users[user_id]['key'] == key
        return curr_post['key'] == key
    else:
        return False


def delete_post(post_id, key):
    """Delete the post with the given ID and key"""
    with lock_request:
        if post_id not in posts:
            error = {'err': f'The post is not found with id: {post_id}'}
            return jsonify(error), HTTPStatus.NOT_FOUND.value
        else:
            if not is_valid_key(post_id, key):
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
        user_id = request.json.get('user_id')
        if user_id is not None:
            if user_id not in users:
                error = {'err': f'Bad request. user_id {user_id} is not exist. Please enter valid user_id.'}
                return jsonify(error), HTTPStatus.BAD_REQUEST.value
            else:
                user_key = request.json.get('user_key')
                if user_key is None:
                    error = {'err': f'Bad request. user key has to be passed if user_id is added.'}
                    return jsonify(error), HTTPStatus.BAD_REQUEST.value
                if is_valid_user_key(user_id, user_key):
                    post = create_post(msg, user_id)
                    return jsonify(post), HTTPStatus.OK.value
                else:
                    error = {'err': f'The user_id {user_id} does not match with key {user_key}'}
                    return jsonify(error), HTTPStatus.FORBIDDEN.value
        if msg is not None:
            post = create_post(msg, None)
            return jsonify(post), HTTPStatus.OK.value
    else:
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


@app.route('/user', methods=['POST'])
def handle_add_user():
    """
    Create user API end point
    metadata: unique user_id, name, phone_num, city
    user object: user_id, name, phone_num, city, created_at, user_key
    :return: creates user with input body info
    """
    if request.is_json:
        if request.json.get('user_id') is None:
            error = {'err': 'Bad request. user_id has to be passed in order to create user'}
            return jsonify(error), HTTPStatus.BAD_REQUEST.value

        if request.json.get('user_id') in users:
            user_id = request.json.get('user_id')
            error = {'err': f'Bad request. user_id {user_id} is already taken. Please use another user_id'}
            return jsonify(error), HTTPStatus.BAD_REQUEST.value

        user = create_user(request.json)
        return jsonify(user), HTTPStatus.OK.value
    else:
        error = {'err': 'Bad request'}
        return jsonify(error), HTTPStatus.BAD_REQUEST.value


@app.route('/user/<string:user_id>', methods=['PUT'])
def handle_update_user(user_id):
    """
    Updates user API end point
    metadata: unique user_id, name, phone_num, city
    user object: user_id, name, phone_num, city, created_at, user_key
    :return: updates metadata of the given user
    """
    if user_id not in users:
        error = {'err': f'user with id {user_id} is found.'}
        return jsonify(error), HTTPStatus.NOT_FOUND.value
    curr_user = update_user(request.json, user_id)
    return jsonify(curr_user), HTTPStatus.OK.value


@app.route('/all-users', methods=['GET'])
def handle_get_all_users():
    return users, HTTPStatus.OK.value


# @app.route('/user/<string:user_id>/keys', methods=['PUT'])
# def handle_generate_user_key(user_id):
#     """
#     Creates new user_key API end point
#     :return: return newly created user_key for a user
#     """
#     if user_id not in users:
#         error = {'err': f'user with id {user_id} is found.'}
#         return jsonify(error), HTTPStatus.NOT_FOUND.value
#     curr_user = generate_new_user_key(user_id)
#     return jsonify(curr_user), HTTPStatus.OK.value


@app.route('/user/<string:user_id>', methods=['GET'])
def handle_get_user(user_id):
    """
    Get user API end point
    :return: returns user for given query param user_id
    """
    if user_id not in users:
        error = {'err': f'user with id {user_id} is found.'}
        return jsonify(error), HTTPStatus.NOT_FOUND.value
    curr_user = get_user(user_id)
    return jsonify(curr_user), HTTPStatus.OK.value


@app.route('/post/user/<string:user_id>', methods=['GET'])
def handle_user_posts(user_id):
    """
    Get user posts by the given user id
    :return: returns posts that posted by the user
    """
    users_posts = []
    if user_id not in users:
        error = {'err': f'user with id {user_id} is found.'}
        return jsonify(error), HTTPStatus.NOT_FOUND.value
    for post in posts:
        if post.get('user_id') is not None and post.get('user_id') == user_id:
            users_posts.append(post)
    return users_posts, HTTPStatus.OK.value
