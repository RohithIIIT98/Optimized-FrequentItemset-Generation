import time

class node:
  def __init__(self):
    self.hash_b={}
    self.descen={}
    self.leaf=True

class c_htree:
  def __init__(self,n_l,n_c):
    self.res=[]
    self.n_l=n_l
    self.n_c=n_c
    self.root=node()
  
  def get_res(self,support_req):
    self.helper_res(self.root,support_req)
    return self.res

  def helper_res(self,curr,support_req):
    if curr.leaf:
      for trans,cnt in curr.hash_b.items():
        if cnt>=support_req:
          self.res.append((list(trans),cnt))
      return
    for index in curr.descen.keys():
      self.helper_res(curr.descen[index],support_req)

  def ins(self,trans):
    self.helper_ins(self.root,tuple(trans),0)

  def helper_ins(self,curr,trans,index):
    if index==len(trans):
      curr.hash_b[trans]=0
      return

    if curr.leaf:
      curr.hash_b[trans]=0
      if len(curr.hash_b)==self.n_l:
        curr.leaf=False
        for temp in curr.hash_b.keys():
          if temp[index]%self.n_c not in curr.descen.keys():
            curr.descen[temp[index]%self.n_c]=node()
          self.helper_ins(curr.descen[temp[index]%self.n_c],temp,index+1)
    else:
      if trans[index]%self.n_c not in curr.descen.keys():
        curr.descen[trans[index]%self.n_c]=node()
      self.helper_ins(curr.descen[trans[index]%self.n_c],trans,index+1)

  
  def fnl_ins(self,trans):
    temp=self.root
    curr=0
    while True:
      if temp.leaf:
        if trans in temp.hash_b:
          temp.hash_b[trans]+=1
        break
      if trans[curr]%self.n_c not in temp.descen.keys():
        break
      temp=temp.descen[trans[curr]%self.n_c]
      curr+=1



import itertools


def freq_itemsets(support_percent,fle1,tot_is):

  fle=open(fle1,'r')
  data=[]
  for lne in fle:
    temp=lne.rstrip('\n').split(' -1 ')
    temp1=list(map(int,temp[:len(temp)-1]))
    temp1.sort()
    data.append(temp1)
    begin=time.time()
  fnl_freq_itemsets=[]
  support_req=int(support_percent/100.0*len(data))
  one_length={}
  for trans in data:
    for val in trans:
      if val in one_length.keys():
        one_length[val]+= 1
      else:
        one_length[val]=1 

      
  candidates_prev_len= []
  for item,cnt in one_length.items():
    if cnt>=support_req:
      candidates_prev_len.append([item])
      fnl_freq_itemsets.append(([item],cnt))


  candidates_prev_len.sort()
  count=0
  # print(len(candidates_prev_len))
  cur_len=2
  while len(candidates_prev_len)>1:
    candidates_cur_len=[]
    for i in range(len(candidates_prev_len)):
      temp=i+1
      while temp<len(candidates_prev_len):
        flag=True
        for t in range(cur_len-2):
          if candidates_prev_len[i][t]!=candidates_prev_len[temp][t]:
            flag=False
            break
        if flag:
          if cur_len==2:
            candidates_cur_len.append([candidates_prev_len[i][-1]]+[candidates_prev_len[temp][-1]])
          else:
            candidates_cur_len.append(candidates_prev_len[i][:-1]+[candidates_prev_len[i][-1]]+[candidates_prev_len[temp][-1]])
        temp+=1

  # print(cur_len,len(candidates_cur_len))

    hobj=c_htree(5,tot_is/10)

    cands_after_pruning=[]
  
    for lst in candidates_cur_len:
      flag=True
      for j in range(cur_len):
        temp=[]
        temp.extend(lst[0:j])
        if j!=cur_len-1:
          temp.extend(lst[j+1:])
        if temp not in candidates_prev_len:
          flag=False
          break
      if flag:
        cands_after_pruning.append(lst)
    
    candidates_cur_len=cands_after_pruning

  # print("after prun",cur_len,len(candidates_cur_len))
  # print(candidates_cur_len)

    for itemset in candidates_cur_len:
      hobj.ins(itemset)

    k_subsets=[]
  #print("done")

    for trans in data:
      k_subsets.extend(itertools.combinations(trans,cur_len))

    for subset in k_subsets:
      if list(subset) in cands_after_pruning:
        hobj.fnl_ins(subset)

    temp_sets=hobj.get_res(support_req)
    fnl_freq_itemsets.extend(temp_sets)
    candidates_prev_len=[]
    for temp in temp_sets:
      candidates_prev_len.append(temp[0])
    candidates_prev_len.sort()
    cur_len+=1

    print("done..")

  end=time.time()

  print("File name:",fle1)
  print("Support_percent:",support_percent,"%")
  print("Number of Frequent Item Sets:",len(fnl_freq_itemsets))
  print("Time taken:",end-begin)
