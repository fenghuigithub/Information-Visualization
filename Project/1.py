#Dingfeng Shao & Nuo Xu
from instagram import client
import sys
import networkx as nx
import matplotlib.pyplot as plt
import instagram
import operator
import time
from prettytable import PrettyTable
import scipy as sp
from Tkinter import *

#login to access user information
def login():
    access_token="560868784.51397a5.973d8aca06ed4308a566e0973b9ddb56"
    api=client.InstagramAPI(access_token=access_token)
    return api




#search user by user name
def search_user(api,user):
    user_id=api.user_search(q=user,count=1)[0].id
    return user_id

#get a list of followings' user_id
def get_following(api,user_id,count):
    user_following,next=api.user_follows(user_id)
    if len(user_following) >= count:
        return [x.id for x in user_following[0:count]]
    else:
        while next:
            following,next=api.user_follows(with_next_url=next)#It returns a url for the next page users
            user_following=user_following+following
            if len(user_following) >=count:
                break
        if len(user_following) >=count:
            return [x.id for x in user_following[0:count]]
        else:
            return [x.id for x in user_following]
    

#get a list of followers' user_id
def get_follower(api,user_id,count):
    user_follower,next=api.user_followed_by(user_id)
    if len(user_follower) >=count:
        return [x.id for x in user_follower[0:count]]
    else:
        while next:
            follower,next=api.user_followed_by(with_next_url=next)#It returns a url for the next page users
            user_follower=user_follower+follower
            if len(user_follower) >=count:
                break
        if len(user_follower)>=count:
            return [x.id for x in user_follower[0:count]]
        else:
            return [x.id for x in user_follower]
'''
to get users' followers count.
Instagram can only check followers count one by one.
'''
def get_count(api,li):
    new_dict={}
    for x in range (0,len(li)):
        try:
            users=api.user(li[x])
            new_dict[li[x]]=users.counts["followed_by"]#return a dictionary with id as key, followers count as value
            time.sleep(0.8)#to prevent rate limit, wait for 0.8s per request
        except instagram.bind.InstagramAPIError as e:
            if e.status_code==400:#error code 400 is for protected users
                continue
            else:
                print e
                continue
        except:#exception for session need. re-login
            e=sys.exc_info()[0]
            print e
            api=login()
            x=x-1
            continue
    return new_dict

#find reciprocal friends and sort the dictionary by value (followers count).
def find_reciprocal(following,follower):
    reciprocal=list(set(following)&set(follower))
    temp=sorted(reciprocal,key=following.get,reverse=True)
    return temp

#the main procedure
def readinfo(user_name,insta):
    print "Start analyzing...",user_name
    user_id=insta.user_search(q=user_name,count=1)[0].id#get user id
    G=nx.Graph()
    G.add_node(user_id)
    queue=[user_id]
    upper=[user_id]
    new=[]
    while len(queue)<=111:#the maximum number of users for 3 level is 111. We need 4 levels.
        for item in upper:           
            following=get_following(insta,item,200)#get first 200 followings
            follower=get_follower(insta,item,200)#get first 200 followers
            following=get_count(insta,following)
            follower=get_count(insta,follower)
            five=find_reciprocal(follower,following)[:10]#find 10 most popular reciprocal friends
            for element in five:
                print element,"  ",follower[element]
                if element in queue:
                    G.add_edge(element,item)
                else:
                    G.add_edge(element,item)
                    new.append(element)
                    queue.append(element)
            print "  "
            five=[]
        upper=[]
        upper.extend(new)
        new=[]    

    print len(queue)

    nx.draw(G)
    plt.savefig('dfs.png')#draw simple graph

    nx.draw_circular(G)
    plt.savefig('circular.png')#draw circular graph

    nx.draw_random(G)
    plt.savefig('random.png')#draw random graph

    nx.draw_spring(G)
    plt.savefig('spring.png')#draw spring graph

    nx.draw_shell(G)
    plt.savefig('shell.png')#draw shell graph

    nx.draw_spectral(G)
    plt.savefig('spectral.png')#draw spectral graph

    nx.write_adjlist(G,"data.adjlist")#record the adjacent list

    #calculate degree centrality, save the table, and get the top 5
    degree=nx.degree_centrality(G)
    sorted_degree=sorted(degree.items(),key=operator.itemgetter(1),reverse=True)
    pt1=PrettyTable(['user_id','data'])
    for label,data in degree.items():
        pt1.add_row([label,data])
    pt1.align['user_id'],pt1.align['data']='l','r'
    pt1.padding_width = 1
    print pt1
    f=open("sorted_degree.txt",'w')
    f.write(pt1.get_string())
    f.close()
    for x in range(0,5):
        print sorted_degree[x][0]

    #calculate closeness centrality, save the table, and get the top 5
    closeness=nx.closeness_centrality(G)
    sorted_closeness=sorted(closeness.items(),key=operator.itemgetter(1),reverse=True)
    pt2=PrettyTable(['user_id','data'])
    for label,data in closeness.items():
        pt2.add_row([label,data])
    pt2.align['user_id'],pt2.align['data']='l','r'
    pt2.padding_width = 1
    print pt2
    f=open("sorted_closeness.txt",'w')
    f.write(pt2.get_string())
    f.close()
    for x in range(0,5):
        print sorted_closeness[x][0]

    #calculate betweenness centrality, save the table, and get the top 5
    betweenness=nx.betweenness_centrality(G)
    sorted_betweenness=sorted(betweenness.items(),key=operator.itemgetter(1),reverse=True)
    pt3=PrettyTable(['user_id','data'])
    for label,data in betweenness.items():
        pt3.add_row([label,data])
    pt3.align['user_id'],pt3.align['data']='l','r'
    pt3.padding_width = 1
    print pt3
    f=open("sorted_betweenness.txt",'w')
    f.write(pt3.get_string())
    f.close()
    for x in range(0,5):
        print sorted_betweenness[x][0]

    #calculate eigenvector centrality, save the table, and get the top 5
    eigenvector=nx.eigenvector_centrality_numpy(G)
    sorted_eigenvector=sorted(eigenvector.items(),key=operator.itemgetter(1),reverse=True)
    pt4=PrettyTable(['user_id','data'])
    for label,data in eigenvector.items():
        pt4.add_row([label,data])
    pt4.align['user_id'],pt4.align['data']='l','r'
    pt4.padding_width = 1
    print pt4
    f=open("sorted_eigenvector.txt",'w')
    f.write(pt4.get_string())
    f.close()
    for x in range(0,5):
        print sorted_eigenvector[x][0]


    #use the linear equation to calculate the score and find the most important friend
    result={}

    for x in range(0,5):
        result[str(sorted_degree[x][0])]=0
        result[str(sorted_closeness[x][0])]=0
        result[str(sorted_betweenness[x][0])]=0
        result[str(sorted_eigenvector[x][0])]=0
    
    for x in range(0,5):
        result[str(sorted_degree[x][0])]=result[str(sorted_degree[x][0])]+5-x
    for x in range(0,5):
        result[str(sorted_closeness[x][0])]=result[str(sorted_closeness[x][0])]+5-x
    for x in range(0,5):
        result[str(sorted_betweenness[x][0])]=result[str(sorted_betweenness[x][0])]+5-x
    for x in range(0,5):
        result[str(sorted_eigenvector[x][0])]=result[str(sorted_eigenvector[x][0])]+5-x
    info=sorted(result,key=result.get,reverse=True)
    for x in range(0,5):
        print "User: "+str(info[x])+"\tscore: "+str(result[str(info[x])])

    
    


if __name__=='__main__':

    user_name=raw_input("Please enter your user name: ")#get user name
    insta=login()#log in
    readinfo(user_name,insta)#start analysis
    
    
    
        
    

    
    












    

