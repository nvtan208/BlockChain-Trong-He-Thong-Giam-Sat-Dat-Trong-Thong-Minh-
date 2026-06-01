"""
deploy.py
Compile Smart Contract và deploy lên Ganache
Chạy 1 lần duy nhất: python deploy.py
"""
from web3 import Web3
from solcx import compile_source, install_solc
import json, os

# ── Cấu hình Ganache ──
GANACHE_URL  = "http://127.0.0.1:7545"
ACCOUNT      = "0xF36F07161CBe665A68E50544f0aee54E2786459A"
PRIVATE_KEY  = "0x12603e3f0ee1421dd683c89b77788714dbdbbd9ffd89e75c4b951909aa64d8ab"
CONTRACT_SOL = os.path.join(os.path.dirname(__file__), "contract", "SmartGarden.sol")
OUTPUT_FILE  = os.path.join(os.path.dirname(__file__), "contract_info.json")

def main():
    # ── Kết nối Ganache ──
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected():
        print("❌ Không kết nối được Ganache! Chạy: ganache --port 7545")
        return
    print("✅ Kết nối Ganache thành công!")
    print(f"   Balance: {w3.eth.get_balance(ACCOUNT) / 1e18:.2f} ETH")

    # ── Cài solc compiler ──
    print("\n📦 Cài Solidity compiler...")
    install_solc("0.8.0")
    print("✅ Solidity 0.8.0 sẵn sàng!")

    # ── Đọc và compile contract ──
    print("\n🔨 Compile Smart Contract...")
    with open(CONTRACT_SOL, "r") as f:
        source = f.read()

    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version="0.8.0"
    )

    contract_id  = "<stdin>:SmartGarden"
    contract_abi = compiled[contract_id]["abi"]
    contract_bin = compiled[contract_id]["bin"]
    print("✅ Compile thành công!")

    # ── Deploy contract ──
    print("\n🚀 Deploy lên Ganache...")
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bin)

    tx = contract.constructor().build_transaction({
        "from":     ACCOUNT,
        "nonce":    w3.eth.get_transaction_count(ACCOUNT),
        "gas":      2000000,
        "gasPrice": w3.eth.gas_price
    })

    signed  = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt.contractAddress
    print(f"✅ Deploy thành công!")
    print(f"   Contract Address: {contract_address}")
    print(f"   Transaction Hash: {tx_hash.hex()}")

    # ── Lưu thông tin contract ──
    info = {
        "contract_address": contract_address,
        "abi":              contract_abi,
        "account":          ACCOUNT,
        "private_key":      PRIVATE_KEY,
        "ganache_url":      GANACHE_URL,
        "tx_hash":          tx_hash.hex()
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(info, f, indent=2)

    print(f"\n💾 Đã lưu thông tin vào: contract_info.json")
    print("\n✅ Sẵn sàng! Chạy: python app.py")

if __name__ == "__main__":
    main()
