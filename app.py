import os
from flask import Flask, render_template, request, redirect
from google import genai
from google.genai import types

app = Flask(__name__)

PROJECT_ID = "dynamic-circle-468209-f9"

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="us-central1",
)

@app.route('/', methods=['GET'])
def index():
    """Render the home page."""
    return render_template('index.html')

def generate(youtube_link, model, additional_prompt):
    """Generate video summary from YouTube link."""
    youtube_video = types.Part.from_uri(
        file_uri=youtube_link,
        mime_type="video/*",
    )

    if not additional_prompt:
        additional_prompt = " "

    contents = [
        youtube_video,
        types.Part.from_text(text="Provide a summary of the video."),
        additional_prompt,
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
    )

    return client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    ).text

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    """Summarize the user-provided YouTube video."""
    if request.method == 'POST':
        youtube_link = request.form['youtube_link']
        model = request.form['model']
        additional_prompt = request.form['additional_prompt']

        try:
            summary = generate(youtube_link, model, additional_prompt)
            return summary
        except ValueError as e:
            return str(e)
    else:
        return redirect('/')

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
