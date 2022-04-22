import socket
import threading
import time


class Proxy:
    def __init__(self):  # 我们要设置一个初始套接字等待客户端的连
        self.client_addr = None
        self.recv_client = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 代表基于IP地址的TCP套接字连接。
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.buffsize = 4096
        self.client_socket.bind(("0.0.0.0", 11111))  # 手机卡绑定手机，可以接听
        self.client_socket.listen(10)  # 最多同时接10个
        self.Host = None
        self.Server_address = None
        self.file_target = None

        # 初始化接听手机完毕。
        # 为什么不初始化打电话的手机呢？因为我们要收到消息之后再打出去。

    def accept_client_socket(self):
        self.recv_client, self.client_addr = self.client_socket.accept()



    def tackle_client_message(self):
        print(threading.currentThread())
        print("从这个套接字接收过来了:{}".format(self.client_addr))
        while True:
            request = self.recv_client.recv(self.buffsize).decode('utf-8')  # 要保证在我们的接受大小之内，并且解码为字符串
            if request:
                print('request timestamp:' +
                      time.strftime("%Y-%m-%d %X", time.localtime()))
                header = request.split("\r\n\r\n")[0]
                message = request.split('\r\n\r\n')[1]
                print(header)  # 消息头

                key_header = {}
                self.file_target = header.split('\r\n')[0]
                print(self.file_target)
                for single_header in header.split('\r\n'):
                    key = single_header.split(':')[0]
                    value = single_header.split(':')[1]
                    if value == None:
                        continue
                        # 不能因为没有值就停下。
                    key_header[key] = value  # 形成键值对。
                self.Host = key_header['Host']
                port = 80
                self.back_to_client(self.connect_server())
            else:
                break
        self.recv_client.close()
        print("关闭了暂时{}的接收".format(self.client_addr))


    def connect_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        (fam, type, _, _, server_address) = socket.getaddrinfo(self.Host.strip(), 80)[0]  # 会得到两个五元组，取第一个代表IPV4
        print(server_address)  # 解析出来的ip地址和端口
        server_socket.connect(server_address)
        response = b''
        recv_msg = b''
        while True:
            msg = "{}\r\nhost:{}\r\nConnection: close\r\n\r\n".format(self.file_target, self.Host.strip())
            server_socket.send(msg.encode('utf-8'))
            print("已发送到服务器")
            recv_msg, address = server_socket.recvfrom(4096)
            print("服务器回应")
            response += recv_msg
            time.sleep(1)
            if recv_msg == b'':
                break
        try:
            print(response.decode('utf-8'))
        except Exception as e:
            pass
        return response

    def back_to_client(self, recv_msg):
        self.recv_client.send(recv_msg)
        print("发送到客户端")

    def run(self):
        while True:
            self.accept_client_socket()
            thread_1 = threading.Thread(target=self.tackle_client_message())
            thread_1.start()
