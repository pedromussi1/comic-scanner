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
    <li><b>Python:</b> Core programming language used for backend logic and AI model integration.</li>
    <li><b>Flask:</b> Lightweight web framework that powers the web server and routes.</li>
    <li><b>TensorFlow / Keras:</b> Deep learning framework used for comic book cover recognition.</li>
    <li><b>OpenCV / NumPy:</b> Used for image processing and numerical computation.</li>
    <li><b>PostgreSQL:</b> Cloud-hosted database for managing user comic collections.</li>
    <li><b>HTML / CSS / JavaScript:</b> Used for creating the front-end interface.</li>
    <li><b>Fly.io:</b> Cloud platform for deploying and hosting the web application.</li>
    <li><b>Google Books API:</b> Provides detailed comic metadata based on search queries.</li>
</ul>

<h2>Environments Used</h2>
<ul>
    <li><b>Windows 11</b></li>
    <li><b>Visual Studio Code</b></li>
</ul>

<h2>Installation</h2>
<ol>
    <li><strong>Clone the Repository:</strong>
        <pre><code>git clone https://github.com/YOUR_USERNAME/comic_book_scanner.git
cd comic_book_scanner</code></pre>
    </li>
    <li><strong>Create and Activate a Virtual Environment:</strong>
        <pre><code>python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`</code></pre>
    </li>
    <li><strong>Install Dependencies:</strong>
        <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Set Environment Variables:</strong>
        <p>Create a <code>.env</code> file in the project root with the following variables:</p>
        <pre><code>DATABASE_URL=your_postgresql_connection_string
GOOGLE_BOOKS_API_KEY=your_api_key_here
FLASK_APP=app.py</code></pre>
    </li>
    <li><strong>Run the Application:</strong>
        <pre><code>flask run</code></pre>
        The application will open automatically at <b>http://127.0.0.1:5000</b>
    </li>
</ol>


<h2>Usage</h2>
<ol>
    <li>Open the web app in your browser.</li>
    <li>Upload or capture a comic book cover image.</li>
    <li>The app analyzes the image using the trained AI model.</li>
    <li>Google Books API fetches detailed information about the comic.</li>
    <li>Click <b>Add to Collection</b> to save the comic in your personal collection.</li>
    <li>Visit the <b>Collection</b> page to browse all your saved comics.</li>
</ol>

<h2>Code Structure</h2>
<ul>
    <li><b>app.py:</b> Main Flask application handling routes and integration.</li>
    <li><b>database.py:</b> Manages PostgreSQL connection and comic collection storage.</li>
    <li><b>model.py:</b> Defines and loads the trained deep learning model for comic recognition.</li>
    <li><b>preprocess.py:</b> Handles image preprocessing and resizing functions.</li>
    <li><b>predict.py:</b> Contains the logic for generating predictions from input images.</li>
    <li><b>utils.py:</b> Helper functions for API calls and data handling.</li>
    <li><b>templates/:</b> HTML templates (index.html, collection.html, edit_button.html).</li>
    <li><b>static/:</b> CSS, JS, and image assets for the front end.</li>
</ul>


<h2>Known Issues</h2>
<ul>
    <li>Low-quality or partially visible comic covers may cause incorrect matches.</li>
    <li>Some older or rare comics may not have metadata available through the Google Books API.</li>
    <li>Large image uploads can slow down recognition performance slightly.</li>
</ul>

<h2>Contributing</h2>
<p>Contributions are welcome! Feel free to fork this repository, make improvements, and open a pull request. For major changes, please open an issue first to discuss your ideas.</p>

<h2>Deployment</h2>
<p>The Comic Book Scanner is deployed on <b>Fly.io</b>, which builds and hosts the application automatically from the repository using a Docker container. To deploy your own instance:</p>
<pre><code>fly launch
fly deploy
</code></pre>

<p>Fly.io automatically builds the container and deploys the Flask web app to a public URL.</p>

<h3>Example Screens</h3>

<h3>Scanning a Comic Cover</h3>
<p align="center">
    <img src="https://i.imgur.com/D2Fejfv.gif" alt="Comic Scanner Interface" width="700">
</p>
<p>The main page allows users to upload or scan comic book covers, which are then analyzed and identified by the AI model.</p>

<hr>

<h3>Viewing Your Comic Collection</h3>
<p align="center">
    <img src="https://i.imgur.com/OuwPnG9.gif" alt="Comic Collection Page" width="700">
</p>
<p>After adding comics, users can view their complete collection with titles, authors, and publication dates retrieved automatically.</p>


