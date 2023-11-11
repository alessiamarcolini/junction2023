from threading import Thread

import eventlet
import executor_service
import user_service


def start_app(app, port):
    eventlet.wsgi.server(eventlet.listen(("", port)), app)


Thread(target=start_app, args=(user_service.app, 5000)).start()
Thread(target=start_app, args=(executor_service.app, 5001)).start()
