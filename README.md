# DNS-server-client
name: Hanning Lin 
date: 02/21/18
## How to compile and run the program
1.open two terminals in the directory of the project.
2.run command "$>python3 DNSServerV3.py" in the first terminal.
3.run command "$>python3 DNSClientV3.py" in the second terminal.

## Notice
1.please use python3 to compile and run the code.
2.Why I used "sSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)" in the 20th line of DNSServerV3.py?
  When closing the TCP connection after the client send the ACK to server, it will wait for 2 MSL to close. Because the previous execution has left the socket in a TIME_WAIT state, and can’t be immediately reused. In oreder to allow the server to be reused, this line of code is used to tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire.

## What exactly the program does
Firstly,the server creat a socket object and waiting for all clients to connect. Secondly, the server creat a new thread to run the monitorQuit function. Since the threads run in parallel, users can exit the server at any time. If the server's socket accept a connection to client, it will open a new thread and creat a new socket object which is used especially for communication to that client. Therefore, the server can serve several clients at the same time. Thirdly, in each thread, the server will first check whether the IP address is in local cache file. If found, it will forward that to the client. If not, it will look up the DNS system using API to find the IP address. If founded, it will be forwarded to client and saved in the cache file to avoid constantly contacting the DNS system for previously resolved problem. If the host name is neither resolve by the local cache nor by the DNS system, "Host not found" will be forwarded to the client side. After the information is sent, the socket will be closed and waiting for another query.
