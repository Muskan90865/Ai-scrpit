from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment - Safe Mode</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment - Safe Mode</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="cookies_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Time Interval in Seconds (e.g., 30)" required><br>
        <button type="submit">Start Safe Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    cookies_file = request.files['cookies_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    cookies_text = cookies_file.read().decode('utf-8')
    comments = comment_file.read().decode('utf-8').splitlines()

    # ✅ Cookies को Dictionary में Convert करना
    cookies = {}
    for line in cookies_text.split(";"):
        if "=" in line:
            key, value = line.strip().split("=", 1)
            cookies[key] = value

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://mbasic.facebook.com/story.php?story_fbid={post_id}"

    user_agents = [
        "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36"
    ]

    def modify_comment(comment):
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌"]
        return comment + " " + random.choice(emojis)

    def get_fb_dtsg():
        """✅ Facebook Page से fb_dtsg Token निकालना"""
        session = requests.Session()
        response = session.get(url, headers={"User-Agent": random.choice(user_agents)}, cookies=cookies)
        if "fb_dtsg" in response.text:
            return response.text.split('name="fb_dtsg" value="')[1].split('"')[0]
        return None

    def post_comment(comment):
        """✅ Cookies से Facebook पर Comment करना"""
        fb_dtsg = get_fb_dtsg()
        if not fb_dtsg:
            return "❌ fb_dtsg Token नहीं मिला!"

        session = requests.Session()
        comment_url = url.replace("story.php?", "a/comment.php?")
        payload = {
            "fb_dtsg": fb_dtsg,
            "jazoest": "2658170097185105",
            "comment_text": modify_comment(comment)
        }

        response = session.post(comment_url, headers={"User-Agent": random.choice(user_agents)}, cookies=cookies, data=payload)

        if response.status_code == 200:
            return "✅ Comment Done!"
        return "❌ Comment Failed!"

    success_count = 0
    for comment in comments:
        result = post_comment(comment)
        print(result)
        if "✅" in result:
            success_count += 1

        time.sleep(interval + random.randint(5, 15))  # **Anti-Ban Delay**

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
