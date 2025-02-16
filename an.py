from flask import Flask, render_template, request
import requests
import time
import random

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_url = request.form["post_url"]
        delay_time = int(request.form["delay_time"])

        # File Handling
        tokens = request.files["tokens_file"].read().decode().splitlines()
        comments = request.files["comments_file"].read().decode().splitlines()

        # Extract Post ID from URL
        post_id = post_url.split("/")[-2]

        for token in tokens:
            comment = random.choice(comments)
            payload = {"message": comment, "access_token": token}
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A)",
                "Accept-Language": "en-US,en;q=0.9",
            }

            response = requests.post(
                f"https://graph.facebook.com/{post_id}/comments",
                data=payload,
                headers=headers,
            )
            
            print(f"Token: {token[:10]}... => Response: {response.json()}")

            # Random Delay to Avoid Detection
            time.sleep(random.randint(delay_time, delay_time + 30))

        return "✅ Comments posted successfully!"

    return """  
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Auto Commenter</title>
    </head>
    <body>
        <h2>Facebook Auto Commenter</h2>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label>Post URL:</label>
            <input type="text" name="post_url" required><br><br>

            <label>Upload Tokens File:</label>
            <input type="file" name="tokens_file" required><br><br>

            <label>Upload Comments File:</label>
            <input type="file" name="comments_file" required><br><br>

            <label>Time Delay (seconds):</label>
            <input type="number" name="delay_time" required><br><br>

            <button type="submit">Start Commenting</button>
        </form>
    </body>
    </html>
    """
    if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
