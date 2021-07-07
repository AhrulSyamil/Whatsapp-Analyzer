from io import BytesIO
import base64
from flask import Flask, render_template, request, json, Response
from flask_cors import CORS

from chat_analytic import chatAnalytics

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index() :
    return render_template('index.html')

@app.route('/test', methods=['GET'])
def test() :
    return "test"

@app.route('/result', methods=["POST"])
def result() :
    request_file = request.files['whatsapp_file']
    
    if not request_file :
        return 'bukan file .txt nih, coba lagi ya'
    
    try :
        chat_whatsapp = chatAnalytics(request_file)

        # make a response json
        response = app.response_class(
            response = json.dumps({
                'device_status': chat_whatsapp.check_device(),
                'detail_chat': chat_whatsapp.detail_chat(),
                'total_chat': chat_whatsapp.total_chat(),
                'content_chat': chat_whatsapp.content(),
                'timeline': chat_whatsapp.timeline(),
                'sentiment_analysis': chat_whatsapp.sentiment_analysis()
            }),
            status = 200,
            mimetype = 'application/json'
        )

        return response
    except Exception as err :
        return err
        # return 'bukan format file dari hasil whatsapp yah'

if __name__ == '__main__' :
    app.run(debug = True)