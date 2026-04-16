from solcx import compile_source, install_solc
import json

install_solc("0.8.0")

with open("blockchain/contract.sol", "r") as file:
    source_code = file.read()

compiled_sol = compile_source(
    source_code,
    output_values=["abi", "bin"],
    solc_version="0.8.0"
)

contract_id, contract_interface = compiled_sol.popitem()

abi = contract_interface["abi"]
bytecode = contract_interface["bin"]

with open("blockchain/abi.json", "w") as f:
    json.dump(abi, f)

with open("blockchain/bytecode.txt", "w") as f:
    f.write(bytecode)

print("ABI and Bytecode generated successfully.")