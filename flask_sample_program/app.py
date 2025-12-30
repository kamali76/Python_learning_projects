from flask import Flask, request, jsonify

app = Flask(__name__) # creates app

@app.route("/health", methods = ["GET"])
def healthCheck():
    return jsonify({"status": "ok"})

@app.route("/add", methods = ["POST"])
def addNumbers():
    data = request.json
    result = int(data["a"]) + int(data["b"])
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug = True)