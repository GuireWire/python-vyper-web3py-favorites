from vyper import compile_code
from dotenv import load_dotenv
from web3 import Web3 #EthereumTesterProvider
import os
from encrypt_key import KEYSTORE_PATH
from eth_account import Account
import getpass

load_dotenv()

RPC_URL = os.getenv("RPC_URL")

# MY_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

def main():
    print("Let's read in the Vyper code and deploy it!")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    # w3 = Web3(Web3.HTTPProvider("https://virtual.sepolia.rpc.tenderly.co/cc770bfc-d956-407f-b5ae-4ea5e204b421")) - This is our fake blockchain on Tenderly
    # w3 = Web3(Web3.HTTPProvider("https://127.0.0.1:8545")) # This is our anvil local chain
    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        compilation_details = compile_code(favorites_code, output_formats=["bytecode", "abi"])
        # print(compilation_details)

    chain_id = 31337 # Make sure this matches your virtual or anvil chain

    print("Getting environment variables...")
    my_address = os.getenv("MY_ADDRESS")

    # private_key = os.getenv("PRIVATE_KEY")
    private_key = decrypt_key(KEYSTORE_PATH)

    # Create the contract in Python
    favorites_contract = w3.eth.contract(abi=compilation_details["abi"], bytecode=compilation_details["bytecode"])
    # print(favorites_contract)
    # breakpoint()
    
    # Submit the transaction that deploys the contract
    nonce = w3.eth.get_transaction_count(my_address)

    # We could do this next line as a shortcut :)
    # tx_hash = favorites_contract.constructor().transact()

    print("Building the transaction...")
    transaction = favorites_contract.constructor().build_transaction(
        { 
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            # "gasPrice": 1
            "from": my_address,
            "nonce": nonce, }
    )
    print("Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("We signed it, check it out:")
    print(signed_txn)

    print("Deploying Contract!")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print("Waiting for transaction to finish...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Done! Contract deployed to {tx_receipt.contractAddress}")

def decrypt_key() -> str:
    with open(KEYSTORE_PATH, "r") as fp:
        encrypted_account = fp.read()
        password = getpass.getpass("Enter your password for your keystore.json:\n")
        key = Account.decrypt(encrypted_account, password)
        print("Decrypted key!")
        return key

    # transaction = {
    # from
    # to etc
    # }
if __name__ == "__main__":
    main()
