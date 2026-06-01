# 🌱 SmartGarden Blockchain

**Hệ thống giám sát đất trồng thông minh với Blockchain + AI**

Tích hợp IoT data từ `garden.db` lên Ethereum Blockchain (Ganache) để đảm bảo tính toàn vẹn dữ liệu, có thể xác minh rằng dữ liệu không bị sửa đổi.

---

## 🎯 Tính Năng

✅ **Blockchain Recording** — Ghi hash dữ liệu lên Smart Contract  
✅ **Data Verification** — Xác minh dữ liệu có bị sửa không  
✅ **Web Dashboard** — Hiển thị lịch sử và thống kê  
✅ **Auto Scheduler** — Tự động ghi mỗi 1 giờ  
✅ **Real-time Status** — Kiểm tra kết nối Ganache  

---

## 🚀 Quick Start

### 1. Cài Đặt

```bash
pip install -r requirements.txt
```

### 2. Deploy Smart Contract

```bash
python deploy.py
```

Lệnh này sẽ:
- Compile `SmartGarden.sol`
- Deploy lên Ganache
- Tạo `contract_info.json` tự động

### 3. Chạy Server

```bash
python app.py
```

Truy cập: **http://localhost:5001**

---

## 📁 Cấu Trúc Project

```
smartgarden_blockchain/
├── app.py                 # Flask server + API
├── blockchain.py          # Web3 helper + Smart Contract interaction
├── deploy.py              # Deploy contract script
├── contract_info.json     # ⚙️ Auto-generated sau deploy
├── requirements.txt       # Dependencies
├── SETUP.md               # Hướng dẫn chi tiết
├── README.md              # File này
│
├── contract/
│   └── SmartGarden.sol    # Smart Contract (Solidity)
│
├── templates/
│   └── index.html         # Web Dashboard UI
│
└── static/
    └── (CSS/JS nếu cần)
```

---

## 🔗 API Reference

### Endpoints

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/` | Web Dashboard |
| GET | `/api/status` | Kiểm tra kết nối |
| GET | `/api/records` | Lấy tất cả records |
| POST | `/api/record_now` | Ghi ngay |
| GET | `/api/verify/<id>` | Xác minh 1 record |
| GET | `/api/verify_all` | Xác minh tất cả |

### Response Example

```json
{
  "status": "ok",
  "tx_hash": "0x...",
  "data_hash": "abc123...",
  "soil_avg": 65,
  "pump_count": 3,
  "ai_decision": "CAN_TUOI",
  "readings": 12
}
```

---

## 🔐 Smart Contract

### RecordData

Ghi dữ liệu vào blockchain:

```solidity
recordData(
  string _dataHash,      // SHA256 hash của data
  uint256 _soilAvg,      // Độ ẩm đất trung bình (%)
  uint256 _pumpCount,    // Số lần bơm nước
  string _aiDecision     // "CAN_TUOI" hoặc "DU_AM"
)
```

### GetRecord

Lấy record từ blockchain:

```solidity
getRecord(uint256 index) returns (
  uint256 timestamp,
  string dataHash,
  uint256 soilAvg,
  uint256 pumpCount,
  string aiDecision
)
```

### VerifyHash

Xác minh hash có khớp không:

```solidity
verifyHash(uint256 index, string _hash) returns (bool)
```

---

## 💾 Database Integration

**Tự động đọc từ:** `../smartgarden/garden.db`

**Các bảng được sử dụng:**

- `readings` — Cảm biến (soil, temp, humidity, pump, ai_result)
- `pump_log` — Lịch sử bơm nước (action, source)

**Query tự động:**
```sql
-- Lấy dữ liệu 1 giờ gần nhất
SELECT * FROM readings 
WHERE ts >= datetime('now', '-1 hour')

SELECT * FROM pump_log 
WHERE ts >= datetime('now', '-1 hour')
```

---

## ⚙️ Cấu Hình

### Ganache Settings

- **URL:** `http://127.0.0.1:8545`
- **Account 0:** `0xCe6b7e7a57cd08Bd3a60BD979eD506cD09180F5e`
- **Private Key:** `0xdc2a5461...` (trong `deploy.py`)

### Flask Settings

- **Host:** `0.0.0.0`
- **Port:** `5001`
- **Debug:** `True`

### Scheduler

Tự động ghi blockchain mỗi **3600 giây (1 giờ)** — có thể chỉnh trong `app.py`:

```python
time.sleep(3600)  # Đổi thành giá trị khác (giây)
```

---

## 🐛 Troubleshooting

### ❌ "Cannot connect to Ganache"

```bash
# Kiểm tra Ganache chạy trên port 8545
http://127.0.0.1:8545

# Nếu Ganache không chạy, khởi động:
ganache --port 8545
```

### ❌ "garden.db not found"

Đường dẫn: `../smartgarden/garden.db`

Nếu cấu trúc thư mục khác, sửa trong `app.py`:

```python
DB_PATH = "/path/to/garden.db"
```

### ❌ "Solidity compile error"

```bash
# Xóa cache compiler
rm -rf ~/.solcx

# Chạy lại deploy
python deploy.py
```

### ❌ "Port 5001 already in use"

Sửa cổng trong `app.py`:

```python
app.run(port=5002)  # Hoặc port khác
```

---

## 📊 Data Flow

```
IoT Sensors
    ↓
garden.db (readings, pump_log)
    ↓
blockchain.py (read & hash)
    ↓
SmartGarden.sol (on-chain storage)
    ↓
Web Dashboard (visualization & verify)
```

---

## 🔑 Workflow Example

1. **Hệ thống IoT chạy** → Lưu dữ liệu vào `garden.db`
2. **Scheduler tự động gọi** (mỗi 1 giờ):
   - Đọc data từ DB
   - Hash bằng SHA256
   - Ghi lên blockchain
3. **Dashboard hiển thị**:
   - Bản ghi mới nhất
   - Thông tin ghi blockchain
4. **Xác minh**:
   - Lấy hash từ blockchain
   - So sánh với hash local
   - Phát hiện data manipulation

---

## 📝 License

MIT

---

## 👨‍💻 Developer Info

- **Solidity Version:** ^0.8.0
- **Python:** 3.8+
- **Web3.py:** >=7.0.0
- **Framework:** Flask 3.0.0

---

**Hỗ trợ:** Xem `SETUP.md` để hướng dẫn chi tiết.
