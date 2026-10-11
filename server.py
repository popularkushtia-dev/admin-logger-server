from flask import Flask, request, render_template_string, jsonify
import time

app = Flask(__name__)

ALL_LOGS = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Remote Monitor Dashboard</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
        h1 { color: #38bdf8; text-align: center; font-size: 24px; margin-bottom: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .log-card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; max-height: 75vh; overflow-y: auto; font-family: 'Consolas', monospace; font-size: 13px; }
        .log-row { padding: 6px 10px; border-bottom: 1px solid #334155; display: flex; gap: 12px; align-items: center; }
        .time { color: #94a3b8; font-size: 12px; }
        .pc { color: #f59e0b; font-weight: bold; background: #292524; padding: 2px 6px; border-radius: 4px; }
        .msg { color: #4ade80; flex-grow: 1; }
        .error { color: #f87171; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ Admin Central Monitoring Panel (Live)</h1>
        <div class="log-card">
            {% for item in logs[::-1] %}
            <div class="log-row">
                <span class="time">[{{ item.time }}]</span>
                <span class="pc">{{ item.pc }}</span>
                <span class="msg {% if 'Error' in item.log or '❌' in item.log %}error{% endif %}">{{ item.log }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/log', methods=['POST'])
def receive_log():
    data = request.get_json()
    if data:
        ALL_LOGS.append(data)
        if len(ALL_LOGS) > 1000:
            ALL_LOGS.pop(0)
        return jsonify({"status": "ok"}), 200
    return jsonify({"error": "No data"}), 400

@app.route('/', methods=['GET'])
def admin_dashboard():
    return render_template_string(HTML_TEMPLATE, logs=ALL_LOGS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
