# Movie Recommender

This project creates a fully functional website that recommends movies to users.

### Features

* Recommends the top 5 related movies, displaying their names and posters.

### Technologies Used

1. **Backend (Python):** `numpy`, `pandas`, `scikit-learn` (sklearn), `tensorflow`, `nltk`

2. **Web Development:** `HTML`, `CSS`, `Flask` (Python web framework)

3. **Deployment:** Render

### Prerequisites

To run this project locally, you will need:

* Python (with `numpy`, `pandas`, `matplotlib`, `scikit-learn` installed)

* A web browser compatible with HTML and CSS

### How to Run Locally

1. **Clone the repository** (if applicable, otherwise copy the files into your local directory).

2. **Open the project** in your preferred code editor.

3. **Install dependencies:**

   ```
   pip install numpy pandas scikit-learn tensorflow nltk flask
   ```

   (Note: `matplotlib` might be needed if you have any plotting scripts, but it's not explicitly listed for the web app itself.)

4. **API Key Configuration:**

   * **Important:** In `app.py`, you will need to change the API key placeholder to your actual TMDb API key.

   * **How to get your API key:**

     1. Log in to the official [TMDb website](https://www.themoviedb.org/).

     2. Navigate to the API section to generate your personal API key.

   * If you encounter issues accessing the API, consider using a VPN.

5. **Run the Flask application:**

   ```
   python app.py
   ```

6. Open your web browser and go to the address displayed in your terminal (usually `http://127.0.0.1:5000/`).

### Deployment

This website is designed for deployment on Render. Follow Render's official documentation for deploying a Flask application.
