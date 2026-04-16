from web3 import Web3
import json

INFURA_URL = "https://sepolia.infura.io/v3/c8616fcbc9ab41119770f2f7b6a0c0d7"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

account = "0x8963370006251ea57193C1843B2704dB0B4a652c"
private_key = "50034b98d289b7d95d993f9dc88b784fc5eb34855e99b6d13c3f851410604856"

with open("blockchain/abi.json") as f:
    abi = json.load(f)

with open("blockchain/bytecode.txt") as f:
    bytecode = f.read()

contract = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.get_transaction_count(account)

transaction = contract.constructor().build_transaction({
    "from": account,
    "nonce": nonce,
    "gas": 2000000,
    "gasPrice": w3.to_wei("10", "gwei")
})

signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print("Deploying contract...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed at:", tx_receipt.contractAddress)