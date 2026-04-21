from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# ------------------ Bias Detection Logic ------------------ #
def detect_bias(text):
    bias_score = 0
    issues = []

    male_words = ["he", "him", "his"]
    female_words = ["she", "her", "hers"]

    male_count = sum(len(re.findall(rf"\b{word}\b", text.lower())) for word in male_words)
    female_count = sum(len(re.findall(rf"\b{word}\b", text.lower())) for word in female_words)

    if male_count > female_count:
        bias_score += 1
        issues.append("Possible male bias detected")
    elif female_count > male_count:
        bias_score += 1
        issues.append("Possible female bias detected")

    # Simple name bias example
    if "john" in text.lower() and "priya" not in text.lower():
        bias_score += 1
        issues.append("Possible name bias detected")

    # Score level
    if bias_score == 0:
        level = "Low"
    elif bias_score == 1:
        level = "Medium"
    else:
        level = "High"

    return {
        "score": level,
        "issues": issues
    }

# ------------------ API ------------------ #
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")
    result = detect_bias(text)
    return jsonify(result)

# ------------------ FRONTEND ------------------ #
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BiasCheck AI</title>
<style>
body {
    font-family: Arial;
    background: #0f172a;
    color: white;
    text-align: center;
    padding: 50px;
}
textarea {
    width: 60%;
    height: 120px;
    padding: 10px;
    border-radius: 10px;
    border: none;
}
button {
    margin-top: 10px;
    padding: 10px 20px;
    background: #22c55e;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
.result {
    margin-top: 20px;
    background: #1e293b;
    padding: 20px;
    border-radius: 10px;
}
</style>
</head>
<body>

<h1>⚖️ BiasCheck AI</h1>
<p>Check if your text contains bias</p>

<textarea id="inputText" placeholder="Paste your text here..."></textarea><br>
<button onclick="analyze()">Analyze</button>

<div class="result" id="result" style="display:none;"></div>

<script>
async function analyze() {
    const text = document.getElementById("inputText").value;

    const res = await fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
    });

    const data = await res.json();

    let output = `<h2>Bias Level: ${data.score}</h2>`;

    if (data.issues.length > 0) {
        output += "<ul>";
        data.issues.forEach(issue => {
            output += `<li>${issue}</li>`;
        });
        output += "</ul>";
    } else {
        output += "<p>No bias detected 🎉</p>";
    }

    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = output;
    resultDiv.style.display = "block";
}
</script>

</body>
</html>
""")

# ------------------ RUN ------------------ #
if __name__ == "__main__":
     app.run(host="0.0.0.0", port=10000)