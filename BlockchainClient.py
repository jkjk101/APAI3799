import requests
import json


class BlockchainClient:
    def __init__(self, host, port, print_response=False):
        self.host = host
        self.port = port
        self.url = f"http://{self.host}:{self.port}"
        self.print_response = print_response

    def _send_get_request(self, endpoint):
        url = self.url + endpoint
        response = requests.get(url)
        return self._process_response(response)

    def _process_response(self, response):
        if response.status_code == 200:
            data = response.json()
            json_string = json.dumps(data, indent=4)
            if self.print_response == True:
                print(json_string)
            return data

    def create_chain(self, id):
        endpoint = f"/create_chain?id={id}"
        return self._send_get_request(endpoint)

    def mine_block(self, id, course_title, course_description, transaction_hash):
        endpoint = f"/mine_block?id={id}&course_title={course_title}&course_description={course_description}&transaction_hash={transaction_hash}"
        return self._send_get_request(endpoint)

    def get_chain(self, id):
        endpoint = f"/get_chain?id={id}"
        return self._send_get_request(endpoint)
    
    def get_prediction(self, id):
        endpoint = f"/get_prediction?id={id}"
        return self._send_get_request(endpoint)

    def check_valid(self, id):
        endpoint = f"/check_valid?id={id}"
        return self._send_get_request(endpoint)

    def print_menu(self):
        print("==============================")
        print("1 - Create new chain")
        print("2 - Mine new block")
        print("3 - Get chain")
        print("4 - Get ESG prediction")
        print("5 - Check validity")
        print("==============================")

    def handle_option(self, option):
        if option == "1":
            id = input("Enter id: ")
            self.create_chain(id)
        elif option == "2":
            id = input("Enter id: ")
            course_title = input("Enter course title: ")
            course_description = input("Enter course description: ")
            transaction_hash = input("Enter transaction hash: ")
            self.mine_block(id, course_title, course_description, transaction_hash)
        elif option == "3":
            id = input("Enter id: ")
            self.get_chain(id)
        elif option == "4":
            id = input("Enter id: ")
            self.get_prediction(id)
        elif option == "5":
            id = input("Enter id: ")
            self.check_valid(id)
        else:
            return False

        return True


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5000
    print_response = True

    client = BlockchainClient(host, port, print_response)

    while True:
        client.print_menu()
        option = input("Enter option: ")

        if not client.handle_option(option):
            continue