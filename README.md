<h1 align="center">📚 Comic Book Scanner</h1>

<p align="center">
  <a href="https://youtu.be/Wwa3Uohue_4"><img src="https://i.imgur.com/RVu12mW.gif" alt="Comic Scanner Demo" width="800"></a>
</p>

<p align="center">A Flask-based web application that identifies comic book covers using image recognition and integrates with the Google Books API to fetch detailed comic information such as title, author, and publication date.</p>

<h3>Try the live app here: <a href="https://comic-scanner.fly.dev/">https://comic-scanner.fly.dev/</a></h3>

<h2>Description</h2>
<p>The **Comic Book Scanner** is an AI-powered web application that allows users to upload or capture images of comic book covers. The system analyzes the image using a trained deep learning model and matches it to the most similar comic from a curated collection. Once identified, it retrieves additional details like title, author, publication date, and cover art via the **Google Books API**. Users can then add comics to their personal online collection and browse them later.This project demonstrates the fusion of **computer vision**, **machine learning**, and **cloud deployment** in building an intelligent and visually interactive web platform.</p>



<h2>Languages and Utilities Used</h2>
<ul>
    <li><b>Python:</b> Core programming language for audio preprocessing, model training, and integration with Streamlit.</li>
    <li><b>Streamlit:</b> Builds the interactive web interface for uploading tracks and displaying predictions.</li>
    <li><b>Librosa:</b> Handles audio loading and extraction of Mel spectrogram features.</li>
    <li><b>TensorFlow/Keras:</b> Trains and loads the convolutional neural network for music genre classification.</li>
    <li><b>Matplotlib / Pillow:</b> Optional visualizations of audio spectrograms.</li>
    <li><b>Soundfile:</b> Enables Streamlit to play uploaded audio files.</li>
</ul>

<h2>Environments Used</h2>
<ul>
    <li><b>Windows 11</b></li>
    <li><b>Visual Studio Code</b></li>
</ul>

<h2>Installation</h2>
<ol>
    <li><strong>Clone the Repository:</strong>
        <pre><code>git clone https://github.com/YOUR_USERNAME/music_genre_classifier.git
cd music_genre_classifier</code></pre>
    </li>
    <li><strong>Create and Activate a Virtual Environment:</strong>
        <pre><code>python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`</code></pre>
    </li>
    <li><strong>Install Dependencies:</strong>
        <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Run the Application:</strong>
        <pre><code>streamlit run app.py</code></pre>
        The application will launch automatically in your browser.
    </li>
</ol>

<h2>Usage</h2>
<ol>
    <li>Open the web application in your browser.</li>
    <li>Upload a short audio track (`.wav` or `.au`).</li>
    <li>The app extracts audio features and predicts the music genre using the trained model.</li>
    <li>View the predicted genre along with confidence scores for each class.</li>
</ol>

<h2>Code Structure</h2>
<ul>
    <li><strong>app.py:</strong> The main Streamlit app file responsible for UI, audio feature extraction, and genre prediction.</li>
    <li><strong>models/music_genre_cnn.keras:</strong> The pre-trained CNN model loaded by the app.</li>
    <li><strong>utils/audio_utils.py:</strong> Functions for loading and preprocessing audio files.</li>
    <li><strong>utils/model_utils.py:</strong> Functions for loading the model and making predictions.</li>
    <li><strong>requirements.txt:</strong> Contains all necessary Python dependencies.</li>
</ul>

<h2>Known Issues</h2>
<ul>
    <li>Only `.wav` and `.au` files are supported for audio uploads.</li>
    <li>Background noise or very short clips may reduce prediction accuracy.</li>
    <li>Live microphone input is not supported on Streamlit Cloud (upload audio instead).</li>
</ul>

<h2>Contributing</h2>
<p>Contributions are welcome! Feel free to fork this repository, make improvements, and open a pull request. For major changes, please open an issue first to discuss your ideas.</p>

<h2>Deployment</h2>
<p>The application is hosted on <b>Streamlit Cloud</b>, which automatically builds the environment based on <code>requirements.txt</code> and serves the app in a web-friendly format. Streamlit handles dependency installation, deployment, and version control integration with GitHub for seamless updates.</p>

<h2><a href="https://github.com/pedromussi1/music_genre_classifier/blob/main/train.py">Model Training Code (optional link)</a></h2>

<h3>Upload Audio</h3>
<p align="center">
    <img src="https://i.imgur.com/OkD0t3r.png" alt="Upload Audio">
</p>
<p>The main interface allows users to upload an audio file. The application then processes the file, extracts features, and predicts the genre.</p>

<hr>

<h3>Genre Prediction Results</h3>
<p align="center">
    <img src="https://i.imgur.com/UcsH7k9.png" alt="Prediction Results">
</p>
<p>After analysis, the application displays the predicted genre and a probability chart representing confidence across different genres.</p>

