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

@app.route('/tokennavigate',methods=['POST'])
def token_navigation():
    # retrieve statement, current position, and navigation command
    stmt = request.json['stmt']
    cur_pos = int(request.json['pos'])
    cmd = request.json['cmd']
    
    print("web token navi api get statement:", stmt, "cur_pos:", cur_pos,
          "cmd:", cmd )

    # navigate based on command
    if cmd == "next":
        next_token = jvox.find_next_token_start(stmt, cur_pos, True)
        print("next token:", next_token)
        dat = {"start": next_token["start"], "stop":next_token["stop"]}
    elif cmd == "pre":
        pre_token = jvox.find_previous_token_start(stmt, cur_pos, True)
        print("previous token:", pre_token)
        dat = {"start": pre_token["start"], "stop":pre_token["stop"]}
    elif cmd == "cur":
        cur_token = jvox.find_cur_token_start_stop(stmt, cur_pos, True)
        print("Current token:", cur_token)
        dat = {"start": cur_token["start"], "stop":cur_token["stop"]}

    return jsonify(dat)


if __name__ == "__main__":
    jvox = jvox_interface.jvox_interface("default")
    print("hello jvox:", jvox)
    # start the web service. this function will not return until the service is
    # terminate. so run this function at the end
    app.run()
    
