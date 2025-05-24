from web3 import Web3
import csv, json, os

# 1) Connect to Ganache Desktop
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.is_connected(), "Ganache not reachable at 7545"

# 2) Load ABI
abi_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "IoTDataStorageABI.json")
with open(abi_path) as f:
    abi = json.load(f)

# 3)  deployed contract address (MAX_ENTRIES=200)
raw_address = "0xF4B97C9C61c2EcEb30780c5750EB95694A703B88"  
contract_address = Web3.to_checksum_address(raw_address)
contract = w3.eth.contract(address=contract_address, abi=abi)

# 4) Use the on-chain owner as default_account
owner = contract.functions.owner().call()
assert owner in w3.eth.accounts, "Owner not in Ganache accounts"
w3.eth.default_account = owner
print(f"✅ Using owner {owner} with {w3.from_wei(w3.eth.get_balance(owner), 'ether')} ETH")

# 5) Read CSV and store Location + Status (2 writes per shipment)
csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "logistics_data.csv")
with open(csv_path, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        if i >= 100:  # 100 shipments × 2 writes = 200 entries
            break

        sid = row["shipment_id"]
        loc = row["destination_city"]
        st  = row["status"]

        # 5a) store Location
        tx1 = contract.functions.storeData(sid, "Location", loc) \
                     .transact({'gas': 200_000})
        w3.eth.wait_for_transaction_receipt(tx1)

        # 5b) store Status
        tx2 = contract.functions.storeData(sid, "Status", st) \
                     .transact({'gas': 200_000})
        w3.eth.wait_for_transaction_receipt(tx2)

        print(f"[{i+1}] Stored {sid}: Location={loc}, Status={st}")

# 6) Final verification
total = contract.functions.getTotalRecords().call()
print("🎉 Done! Total on-chain entries:", total) 
