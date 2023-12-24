from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/speech/<stmt>',methods=['GET'])
def genSpeech(stmt):
    speech = stmt
    print("speech get:", speech)
    return jsonify({'text':speech})

@app.route('/speech2/post',methods=['POST'])
def gen_speech_post():
    dat = {
    'text':"got " + request.json['stmt'],
    }
    print("speech post:", request.json['stmt'])
    print("speech post return:", dat)
    
    return jsonify(dat)

if __name__ == "__main__":
    app.run()
