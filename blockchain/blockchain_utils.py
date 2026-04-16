from web3 import Web3
import json
import os
from config import GANACHE_URL, CONTRACT_INFO_PATH, ABI_PATH

ACCOUNT_ADDRESS = os.environ.get("ACCOUNT_ADDRESS")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")

def get_contract():
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

    with open(CONTRACT_INFO_PATH) as f:
        contract_info = json.load(f)

    contract_address = contract_info["contract_address"]

    with open(ABI_PATH) as f:
        abi = json.load(f)

    contract = w3.eth.contract(address=contract_address, abi=abi)

    return w3, contract


def store_hash_on_blockchain(file_hash):
    w3, contract = get_contract()

    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)

    tx = contract.functions.storeHash(file_hash).build_transaction({
        "from": ACCOUNT_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("10", "gwei")
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt.transactionHash.hex()