
from flask import Flask

app = Flask(__name__)

@app.route('/linxuan')
def hello_world_linxuan():
    return 'Hello World linxuan!'

@app.route('/linxuan2')
def hello_world_linxuan2():
    return 'Hello World linxuan2!'

if __name__ == '__main__':
    app.run()