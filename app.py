from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from src.core.pipeline import rag_pipeline

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = rag_pipeline.run(user_message, session_id)
        return jsonify({
            "response": result["answer"],
            "metadata": {
                "source": result["source"],
                "latency_ms": round(result["latency"] * 1000, 2),
                "hops": result.get("hops", 1)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stream", methods=["POST"])
def stream():
    data = request.json
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    def generate():
        for token in rag_pipeline.run_stream(user_message, session_id):
            yield f"data: {token}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
