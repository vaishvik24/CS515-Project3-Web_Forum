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
