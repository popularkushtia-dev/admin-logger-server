from flask import Flask, request, jsonify

app = Flask(__name__)

# ইন-মেমোরি স্টোরেজ পিসি এবং কাউন্ট ট্র্যাক করার জন্য
active_pcs = {}
ALL_LOGS = []

@app.route('/log', methods=['POST'])
def receive_log():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
    
    pc = data.get("pc", "Unknown")
    time_str = data.get("time", "")
    log_msg = data.get("log", "")
    event_type = data.get("event_type", "log")
    total_saved = data.get("total_saved", 0)
    remaining = data.get("remaining", 0)
    
    # লগ লিস্টে জমা রাখা
    ALL_LOGS.append(data)
    if len(ALL_LOGS) > 1000:
        ALL_LOGS.pop(0)
        
    # পিসি অনুযায়ী স্ট্যাটাস আপডেট
    active_pcs[pc] = {
        "lastSeen": time_str,
        "totalSaved": total_saved,
        "remainingMails": remaining,
        "lastLog": log_msg,
        "eventType": event_type
    }
    
    print(f"[{time_str}] {pc}: {log_msg} (Saved: {total_saved}, Left: {remaining})")
    return jsonify({"status": "ok"}), 200

# এডমিন ড্যাশবোর্ডের জন্য নতুন স্ট্যাটাস API
@app.route('/api/stats', methods=['GET'])
def get_stats():
    grand_total_saved = 0
    grand_total_remaining = 0
    pc_list = []
    
    for pc, info in active_pcs.items():
        grand_total_saved += info["totalSaved"]
        grand_total_remaining += info["remainingMails"]
        pc_list.append({
            "pcName": pc,
            "saved": info["totalSaved"],
            "remaining": info["remainingMails"],
            "lastActive": info["lastSeen"]
        })
        
    return jsonify({
        "totalConnectedPCs": len(active_pcs),
        "grandTotalSaved": grand_total_saved,
        "grandTotalRemaining": grand_total_remaining,
        "pcDetails": pc_list
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Admin Server is Running", "connected_pcs": len(active_pcs)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
