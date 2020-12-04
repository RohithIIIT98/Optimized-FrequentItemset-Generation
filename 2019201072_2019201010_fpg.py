#for time functions
import time

#Function to load file and return lists of Transactions
def loadingData(filename):
    fread=open(filename,'r')
    data=[]
    for line in fread:
      temp=line.rstrip('\n').split(' -1 ')
      temp1=list(temp[:len(temp)-1])
      temp1.sort()
      data.append(temp1)
    return data

#converting to frozenset
def generateInitalSet(dataset):
    frozen_Dictionaries = {}
    for trans in dataset:
      if frozenset(trans) in frozen_Dictionaries:
        frozen_Dictionaries[frozenset(trans)]=frozen_Dictionaries[frozenset(trans)]+1
      else:
        frozen_Dictionaries[frozenset(trans)] = 1
    return frozen_Dictionaries

#class of FP TREE node
class TreeNode:
    def __init__(self, Node_name,counter):
        self.name = Node_name
        self.count = counter
        self.nodeLink = None
        self.children = {}
        
#merging strategy used
def mergingStrategy(conditionalDatabase,Fptree,prevpath):
  for item,subtree in Fptree.children.items():
    current_count=subtree.count
    if item in conditionalDatabase:
      if(len(prevpath)>0):
        k=prevpath.split(",")
        if len(k[0])==0 :
          conditionalDatabase[item][frozenset(k[1:])]=current_count
        else:
          conditionalDatabase[item][frozenset(k)]=current_count
    else:
      conditionalDatabase[item]={}
      if(len(prevpath)>0):
        k=prevpath.split(",")
        if len(k[0])==0 :
          conditionalDatabase[item][frozenset(k[1:])]=current_count
        else:
          conditionalDatabase[item][frozenset(k)]=current_count
    path=prevpath+","+item
    mergingStrategy(conditionalDatabase,subtree,path)

def printfp(Fptree,prevpath):
  for item,subtree in Fptree.children.items():
    path=prevpath+item
    current_count=subtree.count
    print("item",item)
    print(prevpath,current_count)
    printfp(subtree,path)

#To create Headertable and ordered itemsets for FP Tree
def generateFPTree(dataset, minSupport, iterator):
    headerTable = {}

    iterator=iterator+1

    for transaction in dataset:
        for item in transaction:
            headerTable[item] = dataset[transaction] + headerTable.get(item,0) 
    
    for k in list(headerTable):
        if headerTable[k] < minSupport:
            del(headerTable[k])

    frequent_itemset = set(headerTable.keys())

    if len(frequent_itemset) == 0:
        return None, None

    root = TreeNode('Null Set',1)

    for k in headerTable:
        headerTable[k] = [headerTable[k], None]

    for itemset,count in dataset.items():
        frequent_transaction = {}

        for item in itemset:
            if item in frequent_itemset:
                frequent_transaction[item] = headerTable[item][0]
        
        if len(frequent_transaction) >= 1:
            ordered_itemset = [v[0] for v in sorted(frequent_transaction.items(), key=lambda p: p[1], reverse=True)]
            iterator=0
            addTransactionToTree(ordered_itemset, root, headerTable, count , iterator)

    return headerTable,root


def addNodeLink(startNode,targetNode,iterator):
    iterator =iterator+1
    while (startNode.nodeLink != None):
        startNode = startNode.nodeLink
    startNode.nodeLink = targetNode


def addTransactionToTree(itemset, FPTree, headerTable, count ,iterator):
    if itemset[0] in FPTree.children:
        FPTree.children[itemset[0]].count=FPTree.children[itemset[0]].count+count
    else:
        FPTree.children[itemset[0]] = TreeNode(itemset[0], count)

        if headerTable[itemset[0]][1] == None:
            headerTable[itemset[0]][1] = FPTree.children[itemset[0]]
        else:
           iterator = 0
           addNodeLink(headerTable[itemset[0]][1], FPTree.children[itemset[0]],iterator)

    if len(itemset) >= 2:
        addTransactionToTree(itemset[1::], FPTree.children[itemset[0]], headerTable, count ,iterator)


#function to mine recursively conditional patterns base and conditional FP tree
def treeMining(FPTree, headerTable, minSupport, prefix, frequent_itemset,closed_maximum,support_count_subset):

    support_count=[v[1][0] for v in sorted(headerTable.items(),key=lambda p: p[1][0])]
    bigL = [v[0] for v in sorted(headerTable.items(),key=lambda p: p[1][0])]

    #used for merging
    conditionalDatabase={}
    mergingStrategy(conditionalDatabase,FPTree,"")
    all_support_counts=[]

    for i in range(0,len(bigL)):
        
        new_frequentset = prefix.copy()
        new_frequentset.append(bigL[i])

        recursive_purpose_new_frequentset=prefix.copy()
        recursive_purpose_new_frequentset.append(bigL[i])
        
        #add frequent itemset to final list of frequent itemsets
        frequent_itemset[tuple(new_frequentset)]=support_count[i]

        

        if bigL[i] in conditionalDatabase:
          Conditional_pattern_bases=conditionalDatabase[bigL[i]]
        else:
          Conditional_pattern_bases={}

        # if(len(Conditional_pattern_bases)==0):
        #   closed_maximum[tuple(new_frequentset)]=support_count[i]
        
        all_support_counts.append(support_count[i])

        iterator=0

        Conditional_header,Conditional_FPTree = generateFPTree(Conditional_pattern_bases,minSupport,iterator)

        # for finding maximal
        if Conditional_header ==None:
          closed_maximum[tuple(new_frequentset)]=support_count[i]

        if Conditional_header != None:
            treeMining(Conditional_FPTree, Conditional_header, minSupport, recursive_purpose_new_frequentset, frequent_itemset,closed_maximum,support_count[i])
    
    
    #for finding closed item sets
    max_support_count=0
    for j in range(0,len(all_support_counts)):
      if max_support_count< all_support_counts[j] :
        max_support_count=all_support_counts[j]

    superset_found=False

    for super_items,super_support in closed_maximum.items():
      if set(tuple(prefix)).issubset(super_items) and super_support==support_count_subset:
        # print(tuple(prefix),super_items)
        # print(super_support,support_count_subset)
        superset_found=True

    if superset_found==False and support_count_subset>max_support_count  :
      closed_maximum[tuple(prefix)]=support_count_subset

        



print("Enter the filename:")
filename = input()
print("Enter the minimum support count:")
minimumSupport = int(input())

initSet = generateInitalSet(loadingData(filename))

start = time.time()
iterator=0
headerTable,FPtree = generateFPTree(initSet, minimumSupport,iterator)
frequent_itemset = {}
closed_maximum={}
treeMining(FPtree, headerTable, minimumSupport, [], frequent_itemset,closed_maximum,0)
end = time.time()

print("Time Taken for operation is:")
print(end-start)

print("All frequent itemsets:")
print(frequent_itemset)

print(len(frequent_itemset))
print("closed or maximum set",closed_maximum)
print(len(closed_maximum))
