from flask import Flask, request, jsonify
import json
from BlockchainClient import BlockchainClient


class NFTMarketplaceAPI:
    def __init__(self, host, port, BlockchainAPI_port):
        self.host = host
        self.port = port
        self.BlockchainAPI_port = BlockchainAPI_port
        self.BlockchainClient = BlockchainClient(host, BlockchainAPI_port)
        self.app = Flask(__name__)
        self.global_abi = self.load_global_abi()
        self.all_collections = self.load_all_collections()

    def load_global_abi(self):
        # Load the contract's compiled bytecode and ABI
        with open('./contracts/contract.json', 'r') as file:
            contract_data = json.load(file)
        return contract_data['abi']
    
    def get_global_abi(self):
        response = {
            'global_abi': self.global_abi
        }
        return jsonify(response), 200
    
    def load_all_collections(self):
        # Load the object back from the JSON file
        loaded_collections = []
        try:
            with open('./database/collections.json', 'r') as json_file:
                loaded_collections = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(e)
        return loaded_collections

    def dump_all_collections(self):
        # Dump the object to a JSON file
        try:
            with open('./database/collections.json', 'w') as json_file:
                json.dump(self.all_collections, json_file)
        except IOError as e:
            print(e)

    def update_contract_list(self):
        contract_address = request.args.get('contract_address')
        self.all_collections.append(contract_address)
        response = {
            'message': 'Collection list UPDATED',
            'contract_address': contract_address
        }

        self.dump_all_collections()

        return jsonify(response), 200

    def get_contract_list(self):
        response = {
            'all_collections': self.all_collections
        }
        
        return jsonify(response), 200
    
    def get_profile(self):
        wallet_address = request.args.get('wallet_address')
        blockchain = self.BlockchainClient.get_chain(wallet_address)
        ESG_scores = self.BlockchainClient.get_prediction(wallet_address)
        is_valid = self.BlockchainClient.check_valid(wallet_address)

        response = {
            'wallet_address': wallet_address,
            'chain': blockchain['chain'],
            'ESG scores': ESG_scores["ESG scores"],
            'valid': is_valid['message']
        }
        
        return jsonify(response), 200
    
    def update_profile(self):
        wallet_address = request.args.get('wallet_address')
        course_title = request.args.get('course_title')
        course_description = request.args.get('course_description')
        transaction_hash = request.args.get('transaction_hash')

        self.BlockchainClient.mine_block(wallet_address, course_title, course_description, transaction_hash)
        
        response = {
            'message': 'Profile UPDATED',
            'wallet_address': wallet_address,
        }
        
        return jsonify(response), 200
    
    def create_chain_if_not_exist(self):
        wallet_address = request.args.get('wallet_address')
        response = self.BlockchainClient.create_chain(wallet_address)
        
        return jsonify(response), 200


    def run_server(self):
        self.app.route('/get_global_abi', methods=['GET'])(self.get_global_abi)
        self.app.route('/update_contract_list', methods=['GET'])(self.update_contract_list)
        self.app.route('/get_contract_list', methods=['GET'])(self.get_contract_list)
        self.app.route('/get_profile', methods=['GET'])(self.get_profile)
        self.app.route('/update_profile', methods=['GET'])(self.update_profile)
        self.app.route('/create_chain_if_not_exist', methods=['GET'])(self.create_chain_if_not_exist)

        self.app.run(host=self.host, port=self.port)


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5500
    BlockchainAPI_port = 5000

    api = NFTMarketplaceAPI(host, port, BlockchainAPI_port)
    api.run_server()