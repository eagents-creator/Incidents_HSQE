from flask import Flask
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    logger.info("Accessing root route")
    return 'Hello, World!'

@app.route('/test')
def test():
    logger.info("Accessing test route")
    return 'Test page works!'

if __name__ == '__main__':
    logger.info("Starting Flask server on port 8080...")
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
