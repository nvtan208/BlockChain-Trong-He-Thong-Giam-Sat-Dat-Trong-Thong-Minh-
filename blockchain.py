"""
blockchain.py
Helper class tương tác với Smart Contract
"""
from web3 import Web3
import hashlib, json, os, sqlite3
from datetime import datetime

CONTRACT_INFO = os.path.join(os.path.dirname(__file__), "contract_info.json")

class BlockchainHelper:
    def __init__(self):
        with open(CONTRACT_INFO) as f:
            info = json.load(f)

        self.w3           = Web3(Web3.HTTPProvider(info["ganache_url"]))
        self.account      = info["account"]
        self.private_key  = info["private_key"]
        self.contract     = self.w3.eth.contract(
            address=info["contract_address"],
            abi=info["abi"]
        )
        print(f"✅ Blockchain connected: {info['contract_address']}")

    def is_connected(self):
        return self.w3.is_connected()

    def hash_data(self, data_str: str) -> str:
        return hashlib.sha256(data_str.encode()).hexdigest()

    def record_hourly(self, db_path: str) -> dict:
        """Ghi hash toàn bộ data lên Blockchain"""
        try:
            with sqlite3.connect(db_path) as con:
                con.row_factory = sqlite3.Row

                # Lấy TẤT CẢ data từ database
                readings = con.execute("""
                    SELECT * FROM readings
                    ORDER BY id ASC
                """).fetchall()

                pump_logs = con.execute("""
                    SELECT * FROM pump_log
                    ORDER BY id ASC
                """).fetchall()

            if not readings:
                return {"status": "skip", "msg": "Không có data trong database"}

            # Tạo chuỗi data để hash
            data_str   = ""
            soil_total = 0
            for r in readings:
                data_str  += f"{r['ts']},{r['soil']},{r['temp']},{r['humidity']},{r['pump']},{r['ai_result']}|"
                soil_total += r['soil']
            for p in pump_logs:
                data_str += f"{p['ts']},{p['action']},{p['source']}|"

            data_hash  = self.hash_data(data_str)
            soil_avg   = soil_total // len(readings) if len(readings) > 0 else 0
            pump_count = len([p for p in pump_logs if p['action'] == 'on'])
            can_tuoi   = sum(1 for r in readings if r['ai_result'] == 'CAN_TUOI')
            ai_decision = "CAN_TUOI" if can_tuoi > len(readings) // 2 else "DU_AM"

            # Ghi lên Blockchain
            tx = self.contract.functions.recordData(
                data_hash, soil_avg, pump_count, ai_decision
            ).build_transaction({
                "from":     self.account,
                "nonce":    self.w3.eth.get_transaction_count(self.account),
                "gas":      1000000,
                "gasPrice": self.w3.eth.gas_price
            })

            signed  = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                "status":      "ok",
                "tx_hash":     tx_hash.hex(),
                "data_hash":   data_hash,
                "soil_avg":    soil_avg,
                "pump_count":  pump_count,
                "ai_decision": ai_decision,
                "readings":    len(readings)
            }

        except Exception as e:
            return {"status": "error", "msg": str(e)}

    def get_all_records(self) -> list:
        """Lấy tất cả bản ghi từ Blockchain"""
        count   = self.contract.functions.getRecordCount().call()
        records = []
        for i in range(count):
            ts, h, soil, pump, ai = self.contract.functions.getRecord(i).call()
            records.append({
                "index":       i,
                "timestamp":   datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
                "data_hash":   h,
                "soil_avg":    soil,
                "pump_count":  pump,
                "ai_decision": ai
            })
        return records

    def verify(self, db_path: str, index: int) -> dict:
        """Xác minh data có bị sửa không - Đọc TẤT CẢ data giống lúc ghi"""
        try:
            ts, bc_hash, soil, pump, ai = self.contract.functions.getRecord(index).call()

            with sqlite3.connect(db_path) as con:
                con.row_factory = sqlite3.Row
                # Đọc TẤT CẢ data từ database (giống lúc ghi)
                readings = con.execute(
                    "SELECT * FROM readings ORDER BY id ASC"
                ).fetchall()
                pump_logs = con.execute(
                    "SELECT * FROM pump_log ORDER BY id ASC"
                ).fetchall()

            # Tính hash giống hệt lúc ghi
            data_str = ""
            for r in readings:
                data_str += f"{r['ts']},{r['soil']},{r['temp']},{r['humidity']},{r['pump']},{r['ai_result']}|"
            for p in pump_logs:
                data_str += f"{p['ts']},{p['action']},{p['source']}|"

            local_hash = self.hash_data(data_str)
            verified   = (local_hash == bc_hash)

            return {
                "index":            index,
                "timestamp":        datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
                "blockchain_hash":  bc_hash,
                "local_hash":       local_hash,
                "verified":         verified,
                "status":           "✅ Nguyên vẹn" if verified else "❌ Đã bị giả mạo",
                "readings_count":   len(readings)
            }

        except Exception as e:
            return {"status": "error", "msg": str(e)}
