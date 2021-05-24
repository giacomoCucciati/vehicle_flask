from src import create_app, socketio
import logging

logger = logging.getLogger('webgui_logger')
logger.setLevel(logging.DEBUG)

app = create_app(debug=True)

if __name__ == '__main__':
    #try:
    #    socketio.run(app, host="192.168.1.99")
    #except:
    #    print("Running in local? Launching socketio.run(app)")
    socketio.run(app)
