# import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file

# import jupytervox packages
import jvox_interface

app = Flask(__name__)
jvox = None

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

@app.route('/speech3/post',methods=['POST'])
def gen_speech_post_jvox():
    # retrieve statement
    stmt = request.json['stmt']
    print("web api get statement", stmt)

    # generate speech with jvox
    jvox_speech = jvox.gen_speech_for_one(stmt, True)
    print(jvox_speech)

    # generate the mp3 file
    file_name = "/tmp/jvox.mp3"
    jvox.gen_mp3_from_speech(jvox_speech, file_name)
    
    # return the speech
    # return jsonify(jvox_speech)
    return send_file(file_name, mimetype="audio/mpeg")


if __name__ == "__main__":
    jvox = jvox_interface.jvox_interface("default")
    print("hello jvox:", jvox)
    # start the web service. this function will not return until the service is
    # terminate. so run this function at the end
    app.run()
    
