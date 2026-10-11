from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

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
    
    ALL_LOGS.append(data)
    if len(ALL_LOGS) > 1000:
        ALL_LOGS.pop(0)
        
    active_pcs[pc] = {
        "lastSeen": time_str,
        "totalSaved": total_saved,
        "remainingMails": remaining,
        "lastLog": log_msg,
        "eventType": event_type
    }
    
    return jsonify({"status": "ok"}), 200

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

# চমৎকার ডিজাইনের অ্যাডমিন ড্যাশবোর্ড UI
@app.route('/', methods=['GET'])
def home():
    html_template = """
    <!DOCTYPE html>
    html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Central Admin Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            h1 { text-align: center; color: #38bdf8; margin-bottom: 30px; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-left: 5px solid #38bdf8; }
            .card.green { border-left-color: #22c55e; }
            .card.orange { border-left-color: #f59e0b; }
            .card h3 { margin: 0; font-size: 14px; color: #94a3b8; text-transform: uppercase; }
            .card p { font-size: 28px; font-weight: bold; margin: 10px 0 0 0; color: #fff; }
            table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            th, td { padding: 15px; text-align: left; border-bottom: 1px solid #334155; }
            th { background: #334155; color: #38bdf8; text-transform: uppercase; font-size: 12px; }
            tr:hover { background: #273548; }
            .badge { background: #0284c7; color: white; padding: 4px 8px; border-radius: 6px; font-size: 12px; }
            .refresh-note { text-align: center; color: #64748b; margin-top: 20px; font-size: 13px; }
        </style>
        <script>
            async function fetchStats() {
                try {
                    let res = await fetch('/api/stats');
                    let data = await res.json();
                    document.getElementById('pcs').innerText = data.totalConnectedPCs;
                    document.getElementById('saved').innerText = data.grandTotalSaved;
                    document.getElementById('remaining').innerText = data.grandTotalRemaining;
                    
                    let tbody = document.getElementById('pc-table-body');
                    tbody.innerHTML = '';
                    if(data.pcDetails.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b;">কোনো পিসি এখনো কানেক্ট হয়নি</td></tr>';
                    } else {
                        data.pcDetails.forEach(pc => {
                            let tr = document.createElement('tr');
                            tr.innerHTML = `<td><span class="badge">${pc.pcName}</span></td>
                                            <td style="color: #22c55e; font-weight:bold;">${pc.saved}</td>
                                            <td style="color: #f59e0b; font-weight:bold;">${pc.remaining}</td>
                                            <td style="color: #94a3b8; font-size:13px;">${pc.lastActive}</td>`;
                            tbody.appendChild(tr);
                        });
                    }
                } catch(e) { console.log(e); }
            }
            setInterval(fetchStats, 3000);
            window.onload = fetchStats;
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🖥️ Central Admin Monitoring Dashboard</h1>
            <div class="cards">
                <div class="card">
                    <h3>Connected PCs</h3>
                    <p id="pcs">0</p>
                </div>
                <div class="card green">
                    <h3>Total Mails Saved</h3>
                    <p id="saved">0</p>
                </div>
                <div class="card orange">
                    <h3>Total Remaining</h3>
                    <p id="remaining">0</p>
                </div>
            </div>
            
            <h2 style="color: #f1f5f9; font-size: 18px; margin-bottom: 12px;">Worker PCs Status</h2>
            <table>
                <thead>
                    <tr>
                        <th>PC Name</th>
                        <th>Completed (Saved)</th>
                        <th>Remaining</th>
                        <th>Last Active Time</th>
                    </tr>
                </thead>
                <tbody id="pc-table-body">
                    <!-- Dynamic Data -->
                </tbody>
            </table>
            <div class="refresh-note">🔄 Live Auto-Refreshing every 3 seconds...</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
