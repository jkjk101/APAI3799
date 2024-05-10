import requests
import json
from web3 import Web3
from eth_account import Account
import ipfshttpclient
from tabulate import tabulate


class NFTMarketplaceClient:
    def __init__(self, host, port, infura_url):
        self.host = host
        self.port = port
        self.url = f"http://{self.host}:{self.port}"
        self.w3 = Web3(Web3.HTTPProvider(infura_url))  # Connect to an Ethereum node
        self.wallet_address = ""
        self.private_key = ""
        self.global_abi = self.get_global_abi()

    def _send_get_request(self, endpoint):
        url = self.url + endpoint
        response = requests.get(url)
        return self._process_response(response)

    def _process_response(self, response):
        if response.status_code == 200:
            data = response.json()
            return data
        
    def get_global_abi(self):
        endpoint = f"/get_global_abi"
        response = self._send_get_request(endpoint)
        return response["global_abi"]

    def update_contract_list(self, contract_address):
        endpoint = f"/update_contract_list?contract_address={contract_address}"
        return self._send_get_request(endpoint)
    
    def update_profile(self, course_title, course_description, transaction_hash):
        endpoint = f"/update_profile?wallet_address={self.wallet_address}&course_title={course_title}&course_description={course_description}&transaction_hash={transaction_hash}"
        return self._send_get_request(endpoint)
    
    def get_contract_list(self):
        endpoint = f"/get_contract_list"
        response = self._send_get_request(endpoint)
        return response["all_collections"]
        
    def get_profile(self):
        endpoint = f"/get_profile?wallet_address={self.wallet_address}"
        response = self._send_get_request(endpoint)
        return response
    
    def create_chain_if_not_exist(self):
        endpoint = f"/create_chain_if_not_exist?wallet_address={self.wallet_address}"
        response = self._send_get_request(endpoint)
        return response
    
    def login(self):
        wallet_address = input("Enter wallet address: ")
        private_key = input("Enter private key: ")

        # Check if the private key corresponds to the given address
        try:
            account = Account.from_key(private_key)
            if account.address.lower() == wallet_address.lower():
                print("\033[92mLogin success!\033[0m")
                self.wallet_address = wallet_address
                self.private_key = private_key
                self.create_chain_if_not_exist()
            else:
                print("The wallet address and private key do not match.")
                exit()
        except Exception as e:
            print(e)
            exit()
    
    def reconnect(self):
        self.w3 = Web3(Web3.HTTPProvider(infura_url))  # Connect to an Ethereum node
        
    def get_contract(self, contract_address):
        contract = self.w3.eth.contract(address=contract_address, abi=self.global_abi)
        return contract

    def new_collection(self, name, symbol):
        try:
            # Load the contract's compiled bytecode and ABI
            with open('./contracts/contract.json', 'r') as file:
                contract_data = json.load(file)
        
            contract_bytecode = contract_data['byte_code']

            self.reconnect()
            contract = self.w3.eth.contract(abi=self.global_abi, bytecode=contract_bytecode)

            creator = self.wallet_address

            # Build the transaction to deploy the contract
            transaction = contract.constructor(creator, name, symbol).build_transaction({
                    'from': self.wallet_address,
                    'nonce': self.w3.eth.get_transaction_count(self.wallet_address)
                })

            # Sign the transaction with the private key of the deploying account
            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)

            # Send the signed transaction to the network
            transaction_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

            # Wait for the transaction to be mined
            transaction_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)

            # Get the deployed contract address
            contract_address = transaction_receipt['contractAddress']

            self.update_contract_list(contract_address)
            print(f"Contract created: \033[33m{transaction_hash.hex()}\033[0m")

            return contract_address

        except Exception as e:
            print(e)
    
    def mint(self, contract_address, N, uri, price_in_wei, royalty_percentage):
        try:           
            self.reconnect()
            contract = self.get_contract(contract_address)

            transaction = contract.functions.safeMintAndStartSale(N, uri, price_in_wei, royalty_percentage).build_transaction({
                'from': self.wallet_address,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address)
            })

            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            transaction_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                
            print(f"NFT(s) created: \033[33m{transaction_hash.hex()}\033[0m")

            transaction_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
            
        except Exception as e:
            print(e)

    def buy(self, contract_address, tokenId):
        try:
            self.reconnect()
            contract = self.get_contract(contract_address)
            price = contract.functions.sales(tokenId).call()
            token_info = self.get_token_info(contract, tokenId)

            transaction = contract.functions.buyNFT(tokenId).build_transaction({
                'from': self.wallet_address,
                'value': price,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address)
            })

            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            transaction_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

            self.update_profile(token_info[2], token_info[3], transaction_hash.hex())
            print(f"NFT purchased: \033[33m{transaction_hash.hex()}\033[0m")

            transaction_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)

        except Exception as e:
            print(e)
        
    def sale_start(self, contract_address, tokenId, price_in_wei):
        try:
            self.reconnect()
            contract = self.get_contract(contract_address)
            transaction = contract.functions.startSale(tokenId, price_in_wei).build_transaction({
                'from': self.wallet_address,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address)
            })

            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            transaction_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

            print(f"Sale started: \033[33m{transaction_hash.hex()}\033[0m")

            transaction_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        
        except Exception as e:
            print(e)
    
    def sale_cancel(self, contract_address, tokenId):
        try: 
            self.reconnect()
            contract = self.get_contract(contract_address)
            transaction = contract.functions.cancelSale(tokenId).build_transaction({
                'from': self.wallet_address,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address)
            })

            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            transaction_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

            print(f"Sale cancelled: \033[33m{transaction_hash.hex()}\033[0m")

            transaction_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)

        except Exception as e:
            print(e)

    def upload_to_ipfs(self, obj):
        # Connect to IPFS daemon
        client = ipfshttpclient.connect()
        uri = client.add_json(obj)
        uri = f"https://ipfs.io/ipfs/{uri}"
        return uri
    
    def fetch_from_ipfs(self, cid):
        # Connect to IPFS daemon
        client = ipfshttpclient.connect()
        # Fetch the data using the CID
        obj = client.cat(cid)
        obj = obj.decode('utf-8')
        obj = dict(json.loads(obj))
        return obj

    def create(self):
        try:
            contract_address = input("Enter contract address, or 0 to create a new contract: ")
            print()
            if contract_address == "0":
                print("** New collection **")
                print("------------------------------")
                collection_name = input("Enter collection name: ")
                collection_symbol = input("Enter collection symbol: ")
                print("------------------------------")
                contract_address = self.new_collection(collection_name, collection_symbol)
                print()
            
            print("** New NFT(s) **")
            print("------------------------------")
            meta_data = dict()
            meta_data['name'] = input("Enter NFT name: ")
            meta_data['description'] = input("Enter NFT description: ")
            meta_data['external_url'] = input("Enter NFT external url: ")
            N = int(input("Enter number of NFTs: "))
            price = float(input("Enter the initial selling price in ETH: "))
            price_in_wei = Web3.to_wei(price, 'ether')
            royalty_percentage = int(input("Enter NFT royalty percentage: "))
            print("Enter NFT attributes, leave empty to terminate: ")
            attributes = []
            attr_count = 0
            while True:
                trait_type = input(f"\ttrait type #{attr_count}: ")
                if trait_type == "":
                    break
                value = input(f"\tvalue #{attr_count}: ")
                attributes.append(
                    {
                        "trait_type": trait_type, 
                        "value": value
                    })
                attr_count += 1
            meta_data['attributes'] = attributes
            print("------------------------------")

            uri = self.upload_to_ipfs(meta_data)

            self.mint(contract_address, N, uri, price_in_wei, royalty_percentage)

        except Exception as e:
            print(e)

    def get_token_info(self, contract, tokenId):
        try:
            uri = contract.functions.tokenURI(tokenId).call()
            cid = uri.replace('https://ipfs.io/ipfs/', '')
            meta_data = self.fetch_from_ipfs(cid)
            price_in_wei = contract.functions.sales(tokenId).call()
            price = Web3.from_wei(price_in_wei, 'ether')

            token_info = []
            token_info.append(contract.address)
            token_info.append(tokenId)
            token_info.append(meta_data['name'])
            token_info.append(meta_data['description'])
            token_info.append(price)
            token_info.append(contract.functions.royaltyInfo(tokenId, 100).call())
            token_info.append(contract.functions.ownerOf(tokenId).call())
            
            return token_info
        
        except Exception as e:
            print(e)

    def get_all_token_info(self, contract_address):
        try:
            self.reconnect()
            contract = self.get_contract(contract_address)
            total_supply = contract.functions.totalSupply().call()

            all_token_info = []
            for i in range(total_supply):
                token_info = self.get_token_info(contract, i + 1)
                all_token_info.append(token_info[1:])

            return all_token_info
        
        except Exception as e:
            print(e)

    def get_collection_info(self, contract_address):
        try:
            self.reconnect()
            contract = self.get_contract(contract_address)

            collection_info = []
            collection_info.append(contract.address)
            collection_info.append(contract.functions.name().call())
            collection_info.append(contract.functions.symbol().call())
            collection_info.append(contract.functions.owner().call())
            collection_info.append(contract.functions.totalSupply().call())

            return collection_info
        
        except Exception as e:
            print(e)
    
    def get_all_collections_info(self):
        all_collections = self.get_contract_list()

        all_collections_info = []
        for contract_address in all_collections:
            all_collections_info.append(self.get_collection_info(contract_address))

        return all_collections_info
    
    def truncate_string(self, string, max_length):
        if len(string) > max_length:
            return string[:max_length-3] + "..."
        else:
            return string

    def discover(self):
        try:
            headers = ['contract address', 'name', 'symbol', 'creator', 'total supply']
            data = self.get_all_collections_info()
            max_lenegths = [50, 15, len(headers[2]), 50, len(headers[4])]
            truncated_data = [[self.truncate_string(str(data[i][j]), max_lenegths[j]) for j in range(len(data[i]))] for i in range(len(data))]
            table = tabulate(truncated_data, headers=headers, tablefmt="outline")
            print(table)
            print()

            contract_address = input("Enter a contract address, or 0 to return to main menu: ")
            if contract_address == "0":
                return
            print()

            headers = ['token id', 'name', 'description', 'price', '[creator, royalty %]', 'current owner']
            data = self.get_all_token_info(contract_address)
            max_lenegths = [len(headers[0]), 15, 20, len(headers[3]), 50, 50]
            truncated_data = [[self.truncate_string(str(data[i][j]), max_lenegths[j]) for j in range(len(data[i]))] for i in range(len(data))]
            table = tabulate(truncated_data, headers=headers, tablefmt="outline")
            print(table)
            print()

            tokenId = int(input("Enter a token id to buy, or 0 to return to main menu: "))
            if tokenId == 0:
                return
            
            self.buy(contract_address, tokenId)

        except Exception as e:
            print(e)

    def myNFTs(self):
        try:
            all_collections = self.get_contract_list()
            owned_nfts = []

            idx = 1
            for contract_address in all_collections:
                self.reconnect()
                contract = self.get_contract(contract_address)
                total_supply = contract.functions.totalSupply().call()
                for i in range(total_supply):
                    tokenId = i + 1
                    token_info = self.get_token_info(contract, tokenId)

                    if token_info[-1] == self.wallet_address:
                        owned_nfts.append([idx] + token_info[:-1])
                        idx += 1

            headers = ['index', 'contract address', 'token id', 'name', 'description', 'price', '[creator, royalty %]']
            data = owned_nfts
            max_lenegths = [len(headers[0]), 50, len(headers[2]), 15, 20, len(headers[5]), 50]
            truncated_data = [[self.truncate_string(str(data[i][j]), max_lenegths[j]) for j in range(len(data[i]))] for i in range(len(data))]
            table = tabulate(truncated_data, headers=headers, tablefmt="outline")
            print(table)
            print()

            idx = int(input("Enter an index to start or cancel the sale, or 0 to return to main menu: "))
            if idx == 0:
                return

            token = owned_nfts[idx-1]
            if token[5] == 0:   # token[5] is price, token[1] is the contract address, and token[2] is the token id
                price = float(input("Enter a price in ETH to sell: "))
                price_in_wei = Web3.to_wei(price, 'ether')

                self.sale_start(token[1], token[2], price_in_wei)
            else:
                self.sale_cancel(token[1], token[2])

        except Exception as e:
            print(e)

    def profile(self):
        try:
            profile = self.get_profile()

            chain = profile['chain']
            chain = chain[1:]
            ESG_scores = profile['ESG scores']  # 0: total ESG scores, 1: index 1 ESG scores, ...
            is_vaild = True if profile['valid'] == 'The chain is VALID' else False
            
            horizontal_blockchain_data = []
            for block in chain:
                i = block['index']
                formatted_scores = str([float(f"{num:.3f}") for num in ESG_scores[i]])
                horizontal_blockchain_data.append([block['timestamp'], block['data']['course_title'], block['data']['course_description'], block['data']['transaction_hash'], formatted_scores])
            
            headers = ['timestamp', 'title', 'description', 'transaction hash', '[E, S, G]']
            data = horizontal_blockchain_data
            max_lenegths = [20, 15, 20, 80, 25]
            truncated_data = [[self.truncate_string(str(data[i][j]), max_lenegths[j]) for j in range(len(data[i]))] for i in range(len(data))]
            table = tabulate(truncated_data, headers=headers, tablefmt="outline")
            print(table)
            print()

            formatted_scores = [float(f"{num:.3f}") for num in ESG_scores[0]]
            print(f"Total ESG scores: \033[34m{formatted_scores[0]}, {formatted_scores[1]}, {formatted_scores[2]}\033[0m")
            print()

            if is_vaild:
                print("Horizontal blockchain validity: \033[92mVALID\033[0m")
            else:
                print("Horizontal blockchain validity: \033[91mNOT VALID\033[0m")
            
        except Exception as e:
            print(e)

    def print_menu(self):
        self.reconnect()
        logo = '''
              _  _      ___   _____           __  __                    _               _       _ __     _
             | \| |    | __| |_   _|    o O O|  \/  |  __ _      _ _   | |__    ___    | |_    | '_ \   | |    __ _     __      ___
             | .` |    | _|    | |     o     | |\/| | / _` |    | '_|  | / /   / -_)   |  _|   | .__/   | |   / _` |   / _|    / -_)
             |_|\_|   _|_|_   _|_|_   TS__[O]|_|__|_| \__,_|   _|_|_   |_\_\   \___|   _\__|   |_|__   _|_|_  \__,_|   \__|_   \___|
            _|"""""|_| """ |_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|
            "`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'        
        '''
        print()
        print(logo)
        print(f"wallet address: {self.wallet_address}")
        balance_wei = self.w3.eth.get_balance(self.wallet_address)
        balance_eth = Web3.from_wei(balance_wei, 'ether')
        print(f"balance: {balance_eth:.6f} ETH")

        print("==============================")
        print("1 - Create NFTs")
        print("2 - Discover NFT Collections")
        print("3 - My NFTs")
        print("4 - My Learning Profile")
        print("==============================")

    def handle_option(self, option):
        if option == "1":
            self.create()
        elif option == "2":
            self.discover()
        elif option == "3":
            self.myNFTs()
        elif option == "4":
            self.profile()
        else:
            return False
        return True


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5500
    infura_url = "https://sepolia.infura.io/v3/5431fc82aa824806a12a245c4dee3190"

    client = NFTMarketplaceClient(host, port, infura_url)

    client.login()

    while True:
        client.print_menu()
        option = input("Enter option: ")
        print()
        if not client.handle_option(option):
            continue