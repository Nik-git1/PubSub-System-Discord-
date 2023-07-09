import grpc 
import disc_pb2_grpc
import disc_pb2
import uuid

def run():
    channel = grpc.insecure_channel('localhost:50051')
    print("Welcome to the registry client!")
    print("1. Get server list")
    print("2. Join server")
    print("3. Leave server")
    print("4. Publish Articles")
    print("5. Get Articles")
    print("6. ExIT")

    unique_id = str(uuid.uuid1())

    while True:
        choice = input("Enter your choice (1-6): ")
        if choice == "1":
            stub =disc_pb2_grpc.RegisterServiceStub(channel)
            register_request = disc_pb2.void()
            register_response =stub.get_client_list(register_request)
            for value in register_response.server_list:
                print(value.server_name +" localhost:"+ value.server_address)

        elif choice == "2":
            # Handle option 2: Join server    
            # server_address="50053"
            server_address = input("Enter server address: ")
            channel = grpc.insecure_channel('localhost:'+ server_address)
            stub = disc_pb2_grpc.JoinServiceStub(channel)
            client = disc_pb2.JoinReq(client_name=unique_id, server_address=server_address)
            result = stub.join(client)
            print(result.result)
        elif choice == "3":
            server_address = input("Enter server address to leave: ")
            channel = grpc.insecure_channel('localhost:'+ server_address)
            stub = disc_pb2_grpc.JoinServiceStub(channel)
            client = disc_pb2.JoinReq(client_name=unique_id, server_address=server_address)
            result = stub.leave(client)
            print(result)

        elif choice == "4":
            server_address = input("Enter server you want to publish to ")
            #server_address = "50053"
            channel = grpc.insecure_channel('localhost:'+ server_address)
            stub = disc_pb2_grpc.ArticlesServiceStub(channel)
            article_type = input("Enter article type (SPORTS=0, FASHION=1, POLITICS=2): ")
            print(article_type)
            article_type_enum = disc_pb2.ArticleProposal.ArticleType.Value(article_type)
            print(article_type_enum)
            author=input("Enter Author")
            content=input("Enter Content of the Article(200 words max)")
            article = disc_pb2.ArticleProposal(type=article_type_enum,author=author,client_name=unique_id,content=content)
            result = stub.publishArticles(article)
            print(result)
        elif choice == "5":
            server_address = input("Enter server you want to get articles from ")
            channel = grpc.insecure_channel('localhost:' + server_address)
            type_input = input("Enter type of Article [SPORTS, FASHION, POLITICS] (leave blank for all): ")
            author_input = input("Enter author of the Article (leave blank for all): ")
            time_input = input("Enter date of the article (leave blank for all): ")
            if(type_input==""):
                article_type_enum=0
            else:
                 article_type_enum = disc_pb2.ArticleProposal.ArticleType.Value(type_input)
                
            
            article_request = disc_pb2.ArticlesRequest(type=article_type_enum, author=author_input, client_name=unique_id, time=time_input)

            stub = disc_pb2_grpc.ArticlesServiceStub(channel)
            result = stub.getArticles(article_request)
            count=0;

            if(len(result.articles_list) ==0):
                print("failed")
            else:    
                for article in result.articles_list:
                    count=count+1
                    print(count)
                    print(article.type)
                    print(article.author)
                    print(article.time)
                    print(article.content)
                    print('\n')
    
    
        elif choice == "6":
           break 
        else:
            # Handle invalid input
            print("Invalid choice, try again.")   

       
if __name__ == '__main__':
    run()        
