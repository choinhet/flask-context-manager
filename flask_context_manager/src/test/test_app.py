import logging

from flask import Flask

from flask_context_manager import ContextManager

app = Flask(__name__)
ContextManager.append(app)

flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.CRITICAL)

context_manager = logging.getLogger("ContextManager")
context_manager.setLevel(logging.DEBUG)

app_logger = logging.getLogger()
app_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app_logger.addHandler(handler)

if __name__ == '__main__':
    ContextManager.start(debug=True)
