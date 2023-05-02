from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample list of posts
posts = [
    {
        "id": 1,
        "message": "Hello, world!",
        "timestamp": "2022-04-25 10:30:00",
        "user": "Alice"
    },
    {
        "id": 2,
        "message": "Flask is a great web framework!",
        "timestamp": "2022-04-26 14:45:00",
        "user": "Bob"
    },
    {
        "id": 3,
        "message": "Python is my favorite programming language.",
        "timestamp": "2022-04-27 09:15:00",
        "user": "Charlie"
    }
]



#Date- and Time-based range queries 

# Endpoint for searching posts by date/time
@app.route('/posts', methods=['GET'])
def search_posts_date():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not start_time and not end_time:
        return "Please provide at least one parameter (start_time or end_time).", 400
    
    filtered_posts = []
    for post in posts:
        post_time = post['timestamp']
        if start_time and end_time:
            if start_time <= post_time <= end_time:
                filtered_posts.append(post)
        elif start_time:
            if post_time >= start_time:
                filtered_posts.append(post)
        elif end_time:
            if post_time <= end_time:
                filtered_posts.append(post)
    
    return jsonify(filtered_posts)

if __name__ == '__main__':
    app.run(debug=True)



#FULL TEXT SEARCH

# Endpoint for searching posts by a text
@app.route('/posts', methods=['GET'])
def search_posts_text():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No search query provided."}), 400

    results = []
    for post in posts:
        if query.lower() in post['message'].lower():
            results.append(post)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run()


# File upload
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename


@app.route('/api/posts/<post_id>/files', methods=['POST'])
def create_post_files(post_id):
    if post_id not in posts:
        return jsonify({'error': 'Post does not exist'}), HTTPStatus.BAD_REQUEST

    files = request.files.getlist('files')

    if len(files) == 0 and 'files' not in request.json:
        return jsonify({'error': 'Files not found'}), HTTPStatus.BAD_REQUEST

    if 'files' in request.json:
        if not isinstance(request.json['files'], list):
            return jsonify({'error': 'Invalid files payload'}), HTTPStatus.BAD_REQUEST
        file_contents = request.json['files']
        filenames = [f"{post_id}_{str(uuid.uuid4())}.{f.get('extension')}" for f in file_contents]
        for i, content in enumerate(file_contents):
            if 'content' not in content:
                return jsonify({'error': f'Content missing for file {i + 1}'}), HTTPStatus.BAD_REQUEST
            file_data = base64.b64decode(content['content'])
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filenames[i]), 'wb') as f:
                f.write(file_data)
    else:
        filenames = [save_file(f) for f in files]

    if None in filenames:
        return jsonify({'error': 'Invalid file type'}), HTTPStatus.BAD_REQUEST

    posts[post_id]['files'] = filenames
    return jsonify({'message': 'Files uploaded successfully'}), HTTPStatus.OK


@app.route('/api/posts/<post_id>/files', methods=['GET'])
def get_post_files(post_id):
    if post_id not in posts:
        return jsonify({'error': 'Post does not exist'}), HTTPStatus.BAD_REQUEST

    if 'files' not in posts[post_id]:
        return jsonify({'error': 'Files not found for the post'}), HTTPStatus.NOT_FOUND

    file_info = [{'filename': filename} for filename in posts[post_id]['files']]

    if 'metadata' in request.args:
        return jsonify(file_info), HTTPStatus.OK

    file_data = []
    for filename in posts[post_id]['files']:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            file_content = f.read()
        file_data.append({'filename': filename, 'content': base64.b64encode(file_content).decode('utf-8')})
    return jsonify(file_data), HTTPStatus.OK


# Moderator role
lock_request = Lock()

posts = {}
n_bytes = 16
users = {}
moderator_keys = set()  # store moderator keys


def is_valid_username(username):
    pattern = r"^[a-zA-Z0-9]{6,}$"
    return bool(re.match(pattern, username))


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


def get_user(user_id):
    with lock_request:
        curr_user = users.get(user_id)
        if curr_user is not None:
            user_ret = curr_user.copy()
            del user_ret['key']
            return user_ret
        return None


def authenticate_moderator(key):
    return key in moderator_keys


@app.route('/posts', methods=['POST'])
def create_new_post():
    data = request.get_json()
    msg = data.get('msg')
    user_id = data.get('user_id')
    user_key = data.get('user_key')
    if user_id is not None and user_key is not None and is_valid_user_key(user_id, user_key):
        post = create_post(msg, user_id)
        return jsonify(post), HTTPStatus.CREATED
    else:
        return jsonify({'message': 'Invalid user credentials'}), HTTPStatus.UNAUTHORIZED


@app.route('/posts/int:post_id', methods=['GET'])
def get_post(post_id):
    post = posts.get(post_id)
    if post is not None:
        return jsonify(post), HTTPStatus.OK
    else:
        return jsonify({'message': 'Post not found'}), HTTPStatus.NOT_FOUND


@app.route('/users', methods=['POST'])
def create_user_route():
    data = request.get_json()
    user = create_user(data)
    return jsonify(user), HTTPStatus.CREATED


@app.route('/users/string:user_id', methods=['PUT'])
def update_user_route(user_id):
    data = request.get_json()
    if is_valid_username(user_id):
        user = update_user(data, user_id)
        return jsonify(user), HTTPStatus.OK
    else:
        return jsonify({'message': 'Invalid username format'}), HTTPStatus.BAD_REQUEST


@app.route('/users/string:user_id', methods=['GET'])
def get_user_route(user_id):
    user = get_user(user_id)
    if user is not None:
        return jsonify(user), HTTPStatus.OK
    else:
        return jsonify({'message': 'User not found'}), HTTPStatus.NOT_FOUND


@app.route('/moderator/authenticate', methods=['POST'])
def authenticate_moderator_route():
    data = request.get_json()
    key = data.get('key')
    if authenticate_moderator(key):
        moderator_keys.add(key)
        return jsonify({'message': 'Moderator authenticated'}), HTTPStatus.OK
    else:
        return jsonify({'message': 'Invalid moderator key'}), HTTPStatus.UNAUTHORIZED


if __name__ == 'main':
    app.run(debug=True)
