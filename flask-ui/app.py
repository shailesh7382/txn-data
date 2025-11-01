from flask_ui import create_app

app = create_app()

if __name__ == "__main__":
    # Run: python app.py
    app.run(debug=True)
