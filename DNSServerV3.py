# Spring 2018 CSci4211: Introduction to Computer Networks
# This program serves as the server of DNS query.
# Written in Python v3.
# Name: Hanning Lin
# X500: lin00116
# ID: 5454150

import sys, threading, os, random
from socket import *
def main():
	host = "localhost" # Hostname. It can be changed to anything you desire.
	port = 5001 # Port number.

	#create a socket object, SOCK_STREAM for TCP:
	try:
	    sSock=socket(AF_INET,SOCK_STREAM)
	except error as msg:
		print(msg)
		quit()
	sSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)# to tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire. Otherwise, the server can't be reopen in a short time after exit.
	#sSock.setsock
	#bind socket to the current address on port 5001:
	try:
	    sSock.bind((host,port))#bind local IP addresses which is 127.0.0.1 and port which is 5001
	    sSock.listen(20)#Listen on the given socket maximum number of connections queued is 20
	except error as msg:
		print(msg)
		quit
	monitor = threading.Thread(target=monitorQuit, args=[sSock])# open a thread for users to exit the server
	monitor.start()
	print("Server is listening...\n")
	while 1:
		#blocked until a remote machine connects to the local port 5001
		connectionSock, addr = sSock.accept()
		server = threading.Thread(target=dnsQuery, args=[connectionSock, addr[0]])
		#open a thread to do dnsQuery so that the server can serve multiple client at the same time
		server.start()
def dnsQuery(connectionSock, srcAddress):
	print ('Accept new connection from %s...\n' %srcAddress)
	domainName=connectionSock.recv(1024).decode()
	if len(domainName)==0:
		print("Connection Closed.\n")
		connectionSock.close()
		return
	flag=1#flag is used to judge whether the local cache file have the address queried. flag==1 means not found
	#open the local cache file
	try:
		f=open('DNS_Mapping_s18.txt','r+') #open the local cache file for both reading and writing
	except IOError:
		print('file cache doesn\'t exist, creat a new one\n')
		os.mknod('DNS_Mapping_s18.txt')#create a file if it doesn't exist
		f=open('DNS_Mapping_s18.txt','r+')#open the local cache file
	# read the cache file by line and try to find the IP address that client queried
	for line in f.readlines():
		loc=line.find(domainName+":")
		if loc == -1:# if the domain name is not found in that line
			flag=1
		else:
			if loc==0:# if the domain name is found in that line
				flag=0# flag==0 means answer found
				addStr=line[-(len(line)-len(domainName)-1):-1]#addStr is the address in the cache file
				if addStr.find(":")!=-1:# if there are multiple addresses
					alladdr=addStr.split(":")# split the multiple addresses
					addStr=alladdr[0]# choose the first one of the multiple addresses as the answer
				print('      Address found in local cache.\n')
				IPanswer="Local DNS:"+domainName+":"+addStr+"\n"# IPanswer is the answer to the client's query
				connectionSock.send(IPanswer.encode())# send the answer
				print('      Address sent.\n')
				connectionSock.close()# close the socket
				f.close()# close the file
				break
	# if the answer is not in the local cache file. look up in DNS system.
	if flag==1:
			f.close()
			print('No address of this domain name in cache file\n')#!!!!!!temp delet later
			try:# close the file
				addStr=gethostbyname(domainName)# use API to look up in DNS system.
				print('      Address found in DNS system.\n')
				writefile=open('DNS_Mapping_s18.txt','a')# reopen the cache file for appending
				writefile.write(domainName + ':' + addStr + '\n')# add the anwser to local DNS cache
				writefile.close()# close the file
				IPanswer="Root DNS:"+domainName+":"+addStr+"\n"# IPanswer is the answer to the client's query
				connectionSock.send(IPanswer.encode())# send the answer
				print('      Address sent.\n')
				connectionSock.close()# close the socket
			except:# if the answer is not found in DNS system
				print('      Host not found.\n')
				writefile=open('DNS_Mapping_s18.txt','a')# reopen the cache file for appending
				writefile.write(domainName + ':' + 'Host not found' + '\n')# add the error information to local DNS cache
				writefile.close()# close the file
				if domainName.find(".")==-1:#check invalid format
					IPanswer="Host not found. Invalid format, lack of domain suffixes.\n"
				else:
					IPanswer="Host not found. Please recheck the domain name and domain suffixes.\n"
				connectionSock.send(IPanswer.encode())# send the answer
				print('      Address sent.\n')
				connectionSock.close()# close the socket

def monitorQuit(sSock):
	while 1:
		sentence = input()# read the input from
		if sentence == "exit":
			sSock.close()# close the socket opened. if not the port will still be occupied.
			print("Server Shut Down.")
			os.kill(os.getpid(),9)# find the parent's PID and kill the precess tree.
			exit(0);#exit
		else:
			print("Invalid command. Please input \"exit\" to shut down the server.")
main()
