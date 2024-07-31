from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        headers = {
            'User-Agent': 'lataamo-android/225 Dalvik/2.1.0 (Linux; U; iOS 11; iphone-1337) Mobile',
            'Host': 'api.akuankka.fi',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Cookie': 'smf=c484c1375682a2d2c8905113ed2ab8ca; logged_in=1'
        }

        response = requests.get(url, headers=headers)

        try:
            data = response.json()
            # Save data to a JSON file
            json_file_path = os.path.join('static', 'data.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except ValueError as e:
            # Log the response text for debugging purposes
            print("Failed to parse JSON response:", response.text)
            return render_template('index.html', error="Failed to parse JSON response. Please check the URL and try again.")

        return render_template('index.html', data=data, json_file_path=json_file_path)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

