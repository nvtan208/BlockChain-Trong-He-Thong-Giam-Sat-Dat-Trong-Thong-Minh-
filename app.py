"""
app.py — Smart Garden Blockchain
Flask server quản lý Blockchain + Web Dashboard
"""
from flask import Flask, jsonify, render_template, request
from blockchain import BlockchainHelper
import threading, time, os

app = Flask(__name__)
app.json.ensure_ascii = False

# ── Đường dẫn tới garden.db của project IoT ──
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "TPTHONGMINH", "smartgarden", "garden.db")

# ── Khởi tạo Blockchain helper ──
bc = BlockchainHelper()

# ── Scheduler ghi Blockchain mỗi 1 giờ ──
def blockchain_scheduler():
    while True:
        time.sleep(3600)
        print("⏰ Ghi Blockchain tự động...")
        result = bc.record_hourly(DB_PATH)
        print(f"   Result: {result}")

thread = threading.Thread(target=blockchain_scheduler, daemon=True)
thread.start()

# ════════════════════════════════
#  ROUTES
# ════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/records")
def get_records():
    """Lấy tất cả bản ghi từ Blockchain"""
    try:
        records = bc.get_all_records()
        return jsonify({"status": "ok", "records": records, "count": len(records)})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

@app.route("/api/record_now", methods=["POST"])
def record_now():
    """Ghi ngay lập tức lên Blockchain (không chờ 1 giờ)"""
    result = bc.record_hourly(DB_PATH)
    return jsonify(result)

@app.route("/api/verify/<int:index>")
def verify(index):
    """Xác minh bản ghi index có bị sửa không"""
    result = bc.verify(DB_PATH, index)
    return jsonify(result)

@app.route("/api/verify_all")
def verify_all():
    """Xác minh tất cả bản ghi"""
    records = bc.get_all_records()
    results = []
    for r in records:
        v = bc.verify(DB_PATH, r["index"])
        results.append(v)
    total    = len(results)
    ok       = sum(1 for r in results if r.get("verified"))
    return jsonify({
        "total":    total,
        "ok":       ok,
        "failed":   total - ok,
        "results":  results
    })

@app.route("/api/status")
def status():
    return jsonify({
        "connected":   bc.is_connected(),
        "db_exists":   os.path.exists(DB_PATH),
        "record_count": bc.contract.functions.getRecordCount().call()
    })

if __name__ == "__main__":
    print("\n🔗 Smart Garden Blockchain")
    print(f"   Ganache : http://127.0.0.1:8545")
    print(f"   DB Path : {DB_PATH}")
    print(f"   URL     : http://localhost:5001\n")
    app.run(host="0.0.0.0", port=5001, debug=True)
