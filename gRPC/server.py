import grpc 
import disc_pb2_grpc
import disc_pb2
import socket
import sys
from concurrent import futures
from datetime import date
from datetime import datetime

MAXCLIENTS=10

def run(port):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub =disc_pb2_grpc.RegisterServiceStub(channel)
        server_name = input("Enter server name ")
        register_request = disc_pb2.Server(server_name=server_name ,server_address=str(port))
        register_response =stub.register(register_request)
        print(register_response)

CLIENTELE = []
articles =[]
        

class JoinServiceServicer(disc_pb2_grpc.JoinServiceServicer):
    
    def join(self, request, context):
        global CLIENTELE
        print("JOIN REQUEST FROM " +request.client_name )
        join_reply=disc_pb2.Result()
        print(CLIENTELE)
        if(len(CLIENTELE)<MAXCLIENTS):
            CLIENTELE.append(request.client_name)
            join_reply.result="Success"
        else:
            join_reply.result="Failure"

        return join_reply
    
    def leave(self, request, context):
        global CLIENTELE
        print(CLIENTELE)
        print(request.client_name)
        print("Leave Request Made by " +request.client_name )
        leave_reply=disc_pb2.Result()
        CLIENTELE.remove(request.client_name)
        print(CLIENTELE)
        leave_reply.result="Success"
        return leave_reply
    

class ArticleServieServicer(disc_pb2_grpc.ArticlesServiceServicer):

    def publishArticles(self, request, context):
        global CLIENTELE
        global articles

        article_type_str = disc_pb2.ArticleProposal.ArticleType.Name(request.type)

        today=date.today()

        article =disc_pb2.Articles(type=article_type_str,author= request.author,time=str(today),content=request.content)
        print(article)
        
        reply=disc_pb2.Result()    
        if(request.client_name in CLIENTELE):
            articles.append(article)
            print("ARTICLE PUBLISH FROM " +request.client_name )
            reply.result="Success"
        else:
             reply.result="Failure"
                
        return reply


    def getArticles(self, request, context):
        global CLIENTELE
        global articles

        filters = {}
        if request.type:
            filters['type'] = disc_pb2.ArticleProposal.ArticleType.Name(request.type)
        if request.author:
            filters['author'] = request.author
        if request.time:
            filters['time'] = datetime.strptime(request.time, '%Y-%m-%d')

        if request.client_name in CLIENTELE:
            if not filters:
                return disc_pb2.Articles_list(articles_list=articles)
            filtered_articles = []
            for article in articles:
                if all(getattr(article, key) == value for key, value in filters.items()):
                    article_time = datetime.strptime(article.time, '%Y-%m-%d')
                    if not filters.get('time') or article_time >= filters['time']:
                        filtered_articles.append(article)
            return disc_pb2.Articles_list(articles_list=filtered_articles)
        else:
            return disc_pb2.Articles_list()

       
   

def main(port):
    print("server started")
    run(port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    disc_pb2_grpc.add_JoinServiceServicer_to_server(JoinServiceServicer(),server)
    disc_pb2_grpc.add_ArticlesServiceServicer_to_server(ArticleServieServicer(),server)
    server.add_insecure_port('localhost:'+str(port))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python server.py <port>')
        sys.exit(1)
    main(int(sys.argv[1]))