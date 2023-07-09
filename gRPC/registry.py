import disc_pb2
import disc_pb2_grpc
import grpc 
from concurrent import futures

MAXSERVERS=10
class RegisterServiceServicer(disc_pb2_grpc.RegisterServiceServicer):
    def __init__(self):
        self.server_list = []

    def register(self, request, context):
        print("JOIN REQUEST FROM LOCAL HOST:"+request.server_address)
        register_reply=disc_pb2.Result()
        if(len(self.server_list) <MAXSERVERS):        
            self.server_list.append(request)
            register_reply.result="Success"
        else:
            register_reply.result="Failure"
        return register_reply
    
    def get_client_list(self, request, context):
        print("Server List Request")
        return disc_pb2.Server_list(server_list=self.server_list)
    

def main():
    print("server started")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    disc_pb2_grpc.add_RegisterServiceServicer_to_server(RegisterServiceServicer(),server)
    server.add_insecure_port('localhost:50051')
    server.start()
    server.wait_for_termination()

main()    


