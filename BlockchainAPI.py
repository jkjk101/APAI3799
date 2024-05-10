from flask import Flask, request, jsonify
import json
from Blockchain import Blockchain, BlockchainEncoder, BlockchainDecoder
from AI import AI


class BlockchainAPI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.all_chains = self.load_all_chains()
        self.AI = AI()

    def load_all_chains(self):
        # Load the object back from the JSON file
        loaded_chains = []
        try:
            with open('./database/chains.json', 'r') as json_file:
                loaded_chains = json.load(json_file, cls=BlockchainDecoder)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(e)
        return loaded_chains

    def dump_all_chains(self):
        # Dump the object to a JSON file
        try:
            with open('./database/chains.json', 'w') as json_file:
                json.dump(self.all_chains, json_file, cls=BlockchainEncoder)
        except IOError as e:
            print(e)

    def find_chain_by_id(self, id):
        for chain in self.all_chains:
            if chain.id == id:
                return chain
        return None

    def create_chain(self):
        id = request.args.get('id')
        blockchain = self.find_chain_by_id(id)
        
        if blockchain == None:
            blockchain = Blockchain(id)
            blockchain.add_block("Genesis Block")

            self.all_chains.append(blockchain)

            response = {
                'message': 'A chain is CREATED',
                'id': blockchain.id
            }
        else:
            response = {
                'message': 'The chain already EXISTS',
                'id': blockchain.id
            }

        self.dump_all_chains()
        
        return jsonify(response), 200

    def mine_block(self):
        id = request.args.get('id')
        data = {
            'course_title': request.args.get('course_title'),
            'course_description': request.args.get('course_description'),
            'transaction_hash': request.args.get('transaction_hash')
        }

        blockchain = self.find_chain_by_id(id)
        blockchain.add_block(data)

        response = {
            'message': 'A block is MINED',
            'id': blockchain.id,
            'block': blockchain.chain[-1]
        }

        self.dump_all_chains()

        response = json.loads(json.dumps(response, cls=BlockchainEncoder))
        
        return jsonify(response), 200

    def get_chain(self):
        id = request.args.get('id')
        blockchain = self.find_chain_by_id(id)

        response = {
            'id': blockchain.id,
            'chain': blockchain.chain
        }

        response = json.loads(json.dumps(response, cls=BlockchainEncoder))

        return jsonify(response), 200
    
    def get_prediction(self):
        id = request.args.get('id')
        blockchain = self.find_chain_by_id(id)

        response = {
            'id': blockchain.id,
            'ESG scores': self.AI.ESG_scores_prediction(blockchain.chain),
        }
        
        return jsonify(response), 200

    def check_valid(self):
        id = request.args.get('id')
        blockchain = self.find_chain_by_id(id)

        response = {
            'message': 'The chain is VALID' if blockchain.is_chain_valid() else 'The chain is NOT VALID',
        }
        
        return jsonify(response), 200

    def run_server(self):
        self.app.route('/create_chain', methods=['GET'])(self.create_chain)
        self.app.route('/mine_block', methods=['GET'])(self.mine_block)
        self.app.route('/get_chain', methods=['GET'])(self.get_chain)
        self.app.route('/get_prediction', methods=['GET'])(self.get_prediction)
        self.app.route('/check_valid', methods=['GET'])(self.check_valid)

        self.app.run(host=self.host, port=self.port)


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5000

    api = BlockchainAPI(host, port)
    api.run_server()