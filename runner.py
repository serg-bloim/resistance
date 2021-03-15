from bottle import run

from bottleapp import application

run(application, host='localhost', port=7070, debug=True, reloader=True)