from flask import Flask, render_template, request, jsonify
import requests
import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

base_url = 'https://www.akuankka.fi'
directory = os.path.join(os.getcwd(), 'comics')
headers = {
    'User-Agent': 'lataamo-android/225 Dalvik/2.1.0 (Linux; U; Android 13; SM-S911B Build/TP1A.220624.014) Mobile',
    'Host': 'api.akuankka.fi',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'Cookie': 'smf=c484c1375682a2d2c8905113ed2ab8ca; logged_in=1'
}

@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        start = int(request.form['start'])
        end = int(request.form['end'])
        download_comics(start, end)
        return jsonify({"message": f"Downloading from {start} to {end} initiated."})
    return render_template('index.html')

def download_comics(start, end):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for i in range(start, end + 1):
        prefix = f"[{i}/{end}]"
        print(f"{prefix} Downloading Comic #{i}")
        comic_url = f"{base_url}/api/v2/issues/{i}?stories-full=1"
        print(f"{prefix} Requesting {comic_url}")

        try:
            response = requests.get(comic_url, headers=headers)
            response.raise_for_status()
            comic = response.json()
        except Exception as e:
            print(f"{prefix} {str(e)}")
            continue

        current_comic_directory = os.path.join(directory, str(i))
        if not os.path.exists(current_comic_directory):
            os.makedirs(current_comic_directory)

        with open(os.path.join(current_comic_directory, 'issue.json'), 'w') as json_file:
            json.dump(comic, json_file, indent=2)

        for story_index, story in enumerate(comic['stories']):
            story_prefix = f"{prefix}[{story_index + 1}/{len(comic['stories'])}]"
            print(f"{story_prefix} Downloading Story #{story_index + 1} \"{story['title']}\" with {len(story['pages'])} pages")

            for page_index, page in enumerate(story['pages']):
                page_prefix = f"{story_prefix}[{page_index + 1}/{len(story['pages'])}]"
                image_versions = page['images']
                print(f"{page_prefix} Found {len(image_versions)} different Images for page {page_index + 1}")

                for image_version, image_data in image_versions.items():
                    print(f"{page_prefix} Attempting Image Version {image_version}")
                    image_url = base_url + image_data['url']

                    try:
                        image_response = requests.get(image_url, headers=headers, stream=True)
                        image_response.raise_for_status()
                    except Exception as e:
                        print(f"{page_prefix} {str(e)}")
                        continue

                    story_num = story_index + 1
                    page_num = page_index + 1
                    save_path = os.path.join(current_comic_directory, f"Story_{story_num}", f"Page_{page_num}")
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)

                    file_path = os.path.join(save_path, f"{i}_{story_num}_{page_num}_{image_version}{os.path.splitext(image_url)[-1]}")
                    with open(file_path, 'wb') as image_file:
                        for chunk in image_response.iter_content(1024):
                            image_file.write(chunk)

if __name__ == '__main__':
    app.run(debug=True)

