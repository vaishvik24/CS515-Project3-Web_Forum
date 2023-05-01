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
