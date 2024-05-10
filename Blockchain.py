from hashlib import sha256
from datetime import datetime
from json import JSONEncoder, JSONDecoder


class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash

    def calculate_hash(self):
        return sha256(
            str(self.index).encode('utf-8') +
            str(self.timestamp).encode('utf-8') +
            str(self.data).encode('utf-8') +
            str(self.previous_hash).encode('utf-8') +
            str(self.nonce).encode('utf-8')
        ).hexdigest()

    def calculate_hash_with_proof(self, difficulty=4):
        while True:
            hash_value = self.calculate_hash()

            if hash_value[:difficulty] == "0" * difficulty:
                return hash_value

            self.nonce += 1
    

class Blockchain:
    def __init__(self, id):
        self.id = id
        self.chain = []

    def add_block(self, data):
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data=data,
            previous_hash=self.chain[-1].hash if data != "Genesis Block" else "0"*64
        )
        new_block.hash = new_block.calculate_hash_with_proof()

        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            print(current_block.hash, current_block.calculate_hash())
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False

        return True


class BlockEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Block):
            return {
                'index': obj.index,
                'timestamp': obj.timestamp,
                'data': obj.data,
                'previous_hash': obj.previous_hash,
                'nonce': obj.nonce,
                'hash': obj.hash
            }
        return super().default(obj)


class BlockDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if 'index' in dct and 'timestamp' in dct and 'data' in dct and 'previous_hash' in dct and 'nonce' in dct and 'hash' in dct:
            index = dct['index']
            timestamp = dct['timestamp']
            data = dct['data']
            previous_hash = dct['previous_hash']
            nonce = dct['nonce']
            hash = dct['hash']
            return Block(index, timestamp, data, previous_hash, nonce, hash)
        return dct
    

class BlockchainEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Blockchain):
            return {
                'id': obj.id,
                'chain': obj.chain
            }
        elif isinstance(obj, Block):
            return BlockEncoder().default(obj)

        return super().default(obj)
    
    
class BlockchainDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if 'id' in dct and 'chain' in dct:
            blockchain = Blockchain(dct['id'])
            blockchain.chain = self.decode_blockchain(dct['chain'])
            return blockchain
        return dct

    def decode_blockchain(self, chain):
        blockDecoder = BlockDecoder()
        decoded_blocks = []
        for block in chain:
            if isinstance(block, dict):
                decoded_block = blockDecoder.object_hook(block)
            else:
                decoded_block = block
            decoded_blocks.append(decoded_block)
        return decoded_blocks