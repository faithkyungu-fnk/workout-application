from flask import Flask, jsonify
from flask_migrate import Migrate
from server.models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

 #connecting the db and migration to the app
    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the Fitness App!"})

    return app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)