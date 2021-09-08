from flask import Flask, request, Response

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return "The page you are looking for can't be found", 404

@app.route("/hello", methods=['GET'])
def hello():
    msg = request.args.get('msg', default = "", type = str)
    return Response(f"Hello {msg}", status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9080, debug=True)
