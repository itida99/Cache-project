from prettytable import PrettyTable
import sys
import random
def binary(n,bits):
    if(n==0):
        l = [0]
        l = make_n_bits(l,bits)
        return ''.join([str(elem) for elem in l])
    if(n>0):
        l=[]
        while(n>1):
            l.append(n%2)
            n=n//2
        l.append(1)
        l.reverse()
        l = make_n_bits(l,bits)
        return ''.join([str(elem) for elem in l])
def make_n_bits(l,n):
    l.reverse()
    while(len(l)<n):
        l.append(0)
    l.reverse()
    return l
def decimal(l):
    l = list(l)
    ans = 0
    j = 0
    for i in l[::-1]:
        ans+=int(i)*(2**j)
        j+=1
    return ans

class DirectMapping:
    def __init__(self,memorySize, blockOffsetBits, cacheIndexBits,dataType):
        #chechk N is greater than other two
        self.memorySize = memorySize 
        self.blockOffsetBits = blockOffsetBits
        self.cacheIndexBits = cacheIndexBits
        self.blockIndexBits = self.memorySize - blockOffsetBits
        self.cacheAddressBits = cacheIndexBits + blockOffsetBits
        self.tagBits = self.memorySize - self.cacheAddressBits
        self.memoryData = 'rndm' if dataType == 1 else random.randint(-2147483648,2147483647)
        self.cache = [['' if j== 0 else '' for j in range((2**blockOffsetBits)+1)] for i in range(2**cacheIndexBits)]
        self.printCache()
    def read(self,address,other=-1):
        hitMiss = self.hitOrMiss(address)
        tag = address[0:self.tagBits]
        blockIndex = address[self.tagBits:(self.tagBits+self.cacheIndexBits)]
        blockOffset = address[self.tagBits+self.cacheIndexBits:]
        blockIndex = decimal(blockIndex)
        blockOffset = decimal(blockOffset)
        if(other !=-1):
            if hitMiss:
                data = self.cache[blockIndex][blockOffset+1] 
                print('There was a read hit in L1 and the data at the address:',address,'is',data)
            else:
                l,b = other.returnBlock(address)
                prevAddress = self.cache[blockIndex][0] 
                t = other.cache[b][0]
                if(l[0]==tag):
                    self.cache[blockIndex] = [tag if j==0 else l[j] for j in range((2**self.blockOffsetBits)+1)]
                    print('read hit in L2 but miss in L1 and line replaced in L1 tag:',prevAddress)
                else:  
                    self.cache[blockIndex] = [tag if j==0 else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    other.cache[b] = [tag if j==0 else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    print('read miss in L2 and in L1 and replaced tag:',t,'L2 and tag:',prevAddress,'in L1')               
        else:
            if hitMiss:
                data = self.cache[blockIndex][blockOffset+1] 
                print('There was a read hit and the data at the address:',address,'is',data)
            else:
                prevAddress = self.cache[blockIndex][0]
                self.cache[blockIndex] = [tag if j==0 else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                print('There was a read miss and the new tag has replaced the tag:',prevAddress,'and data of new block has been initialized with random data ')
        self.printCache()
    def write(self,address,data,other=-1):
        hitMiss = self.hitOrMiss(address)
        tag = address[0:self.tagBits]
        blockIndex = address[self.tagBits:(self.tagBits+self.cacheIndexBits)]
        blockOffset = address[self.tagBits+self.cacheIndexBits:]
        blockIndex = decimal(blockIndex)
        blockOffset = decimal(blockOffset)
        if other == -1:
            if hitMiss:
                self.cache[blockIndex][blockOffset+1] = data 
                print('There was a write hit and the data at the address:',address,'has been updated')
            else:
                prevAddress = self.cache[blockIndex][0]
                self.cache[blockIndex] = [tag if j==0 else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                self.cache[blockIndex][blockOffset+1] = data
                print('There was a write miss and the new address has replaced the address:',prevAddress,'and data of new address has been updated ')
        else:
            if hitMiss:
                self.cache[blockIndex][blockOffset+1] = data 
                print('There was a write hit and the data at the address:',address,'has been updated')
            else:
                l,b = other.returnBlock(address)
                prevAddress = self.cache[blockIndex][0] 
                t = other.cache[b][0]
                if(l[0]==tag):
                    self.cache[blockIndex] = [tag if j==0 else l[j] for j in range((2**self.blockOffsetBits)+1)]
                    self.cache[blockIndex][blockOffset+1] = data
                    other.cache[b][blockOffset+1] = data
                    print('write hit in L2 but miss in L1 updated data in L1 and in L2')
                else:  
                    self.cache[blockIndex] = [tag if j==0 else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    other.cache[b] = [tag if j==0 else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    self.cache[blockIndex][blockOffset+1] = data
                    other.cache[b][blockOffset+1] = data
                    print('write miss in L2 and in L1 and replaced tag:',t,'L2 and tag:',prevAddress,'in L1 and updated data in both')
        self.printCache()
    def hitOrMiss(self,address):
        #check adress is of correct bits
        tag = address[0:self.tagBits]
        blockIndex = address[self.tagBits:(self.tagBits+self.cacheIndexBits)]
        blockIndex = decimal(blockIndex)
        if(self.cache[blockIndex][0]==tag):
            return True
        else:
            return False
    def printCache(self):
        t = PrettyTable(['Tag','Cache Line',*[binary(j,self.blockOffsetBits) for j in range(2**self.blockOffsetBits)]])
        for i in range(2**self.cacheIndexBits):
            t.add_row([self.cache[i][0],binary(i,self.cacheIndexBits),*self.cache[i][1:]])
        print(t)
    def returnBlock(self,address):
        blockIndex = address[self.tagBits:(self.tagBits+self.cacheIndexBits)]
        blockIndex = decimal(blockIndex)
        return self.cache[blockIndex],blockIndex
class AssociativeMapping:
    def __init__(self,memorySize, blockOffsetBits, cacheIndexBits,dataType):
        #chechk N is greater than other two
        self.memorySize = memorySize 
        self.blockOffsetBits = blockOffsetBits
        self.cacheIndexBits = cacheIndexBits
        self.blockIndexBits = self.memorySize - blockOffsetBits
        self.tagBits = self.blockIndexBits
        self.memoryData = 'rndm' if dataType == 1 else random.randint(-2147483648,2147483647)
        self.cache = dict()
        self.printCache()
    def write(self,address,data,other=-1):
        tag = address[0:self.tagBits]
        blockOffset = address[self.tagBits:]
        blockOffset = decimal(blockOffset)
        if(other==-1):
            if tag in self.cache:
                self.cache[tag][blockOffset] = data
                self.cache[tag][2**self.blockOffsetBits]+=1
                print('There was a write hit and the data at the address has been updated ')
            else:
                if(len(self.cache)>=2**self.cacheIndexBits):
                    prevAddress = self.findLFR()
                    l = [self.memoryData if j!=blockOffset and j!= 2**self.blockOffsetBits else 1 if j==2**self.blockOffsetBits else data for j in range((2**self.blockOffsetBits)+1)]
                    self.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in self.cache.items()}
                    print('There was a write miss and the new tag has replaced the tag:',prevAddress,'and data of new address has been updated ')
                else:
                    self.cache[tag] = [self.memoryData if j!=blockOffset and j!= 2**self.blockOffsetBits else 1 if j==(2**self.blockOffsetBits) else data for j in range((2**self.blockOffsetBits)+1)]
                    self.cache[tag][blockOffset] = data
                    print('There was a write miss and a new tag has been added to a not yet full cache and the data at the address has been updated ')
        else:
            if tag in self.cache:
                self.cache[tag][blockOffset] = data
                self.cache[tag][2**self.blockOffsetBits]+=1
                print('There was a write hit in L1 and the data at the address has been updated')
            else:
                if tag in other.cache:
                    print('write miss in L1 but hit in L2')
                    if(len(self.cache)>=2**self.cacheIndexBits):
                        prevAddress = self.findLFR()
                        l = [1 if j==2**self.blockOffsetBits else other.cache[tag][j] for j in range((2**self.blockOffsetBits)+1)]
                        self.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in self.cache.items()}
                        self.cache[tag][blockOffset] = data
                        other.cache[tag][blockOffset] = data
                        other.cache[tag][2**self.blockOffsetBits]+=1
                        print('new tag replaced the tag:',prevAddress,'and data of new address has been initialized with random data ')
                    else:
                        self.cache[tag] = [1 if j==2**self.blockOffsetBits else other.cache[tag][j] for j in range((2**self.blockOffsetBits)+1)]
                        self.cache[tag][blockOffset] = data
                        other.cache[tag][blockOffset] = data
                        other.cache[tag][2**self.blockOffsetBits]+=1
                        print('a new tag has been added to a not yet full cache L1 and data has been updated')
                else:
                    print('write miss in L1 and miss in L2')
                    if(len(other.cache)>=2**other.cacheIndexBits):
                        prevAddress = other.findLFR()
                        l = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in other.cache.items()}
                        other.cache[tag][blockOffset] = data
                        print(' new tag has replaced the tag:',prevAddress,'in L2 and data has been updated')
                    else:
                        other.cache[tag] = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache[tag][blockOffset] = data
                        print('new tag has been added to a not yet full cache L2 and data has been updated')
                    if(len(self.cache)>=2**self.cacheIndexBits):
                        prevAddress = self.findLFR()
                        l = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        self.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in self.cache.items()}
                        self.cache[tag][blockOffset] = data
                        print(' new tag has replaced the tag:',prevAddress,'in L1 and data has been updated')
                    else:
                        self.cache[tag] = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        self.cache[tag][blockOffset] = data
                        print('new tag has been added to a not yet full cache L1 and data has been updated')
        self.printCache()
    def read(self,address,other=-1):
        tag = address[0:self.tagBits]
        blockOffset = address[self.tagBits:]
        blockOffset = decimal(blockOffset)
        if(other == -1):
            if tag in self.cache:
                data = self.cache[tag][blockOffset] 
                self.cache[tag][2**self.blockOffsetBits]+=1
                print('There was a read hit and the data at the address:',address,'is',data)
            else:
                if(len(self.cache)>=2**self.cacheIndexBits):
                    prevAddress = self.findLFR()
                    l = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    self.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in self.cache.items()}
                    print('There was a read miss and the new tag has replaced the tag:',prevAddress,'and data of new address has been initialized with random data ')
                else:
                    self.cache[tag] = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    print('There was a read miss and a new tag has been added to a not yet full cache and random data has been loaded from the memory')
        else:
            if tag in self.cache:
                data = self.cache[tag][blockOffset] 
                self.cache[tag][2**self.blockOffsetBits]+=1
                print('There was a read hit in L1 and the data at the address:',address,'is',data)
            else:
                if tag in other.cache:
                    print('read miss in L1 but hit in L2')
                    if(len(self.cache)>=2**self.cacheIndexBits):
                        prevAddress = self.findLFR()
                        l = [1 if j==2**self.blockOffsetBits else other.cache[tag][j] for j in range((2**self.blockOffsetBits)+1)]
                        self.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in self.cache.items()}
                        other.cache[tag][2**self.blockOffsetBits]+=1
                        print('new tag replaced the tag:',prevAddress,'and data of new address has been initialized with random data ')
                    else:
                        self.cache[tag] = [1 if j==2**self.blockOffsetBits else other.cache[tag][j] for j in range((2**self.blockOffsetBits)+1)]
                        other.cache[tag][2**self.blockOffsetBits]+=1
                        print('a new tag has been added to a not yet full cache L1')
                else:
                    print('read miss in L1 and miss in L2')
                    if(len(other.cache)>=2**other.cacheIndexBits):
                        prevAddress = other.findLFR()
                        l = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in other.cache.items()}
                        print(' new tag has replaced the tag:',prevAddress,'in L2')
                    else:
                        other.cache[tag] = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        print('new tag has been added to a not yet full cache L2')
                    if(len(self.cache)>=2**self.cacheIndexBits):
                        prevAddress = self.findLFR()
                        l = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        self.cache = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in self.cache.items()}
                        print(' new tag has replaced the tag:',prevAddress,'in L1')
                    else:
                        self.cache[tag] = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        print('new tag has been added to a not yet full cache L1')
        self.printCache()
    def findLFR(self):
        minimum = float('inf')
        leastKey = ''
        for key,values in self.cache.items():
            if(values[2**self.blockOffsetBits]<minimum):
                minimum = values[2**self.blockOffsetBits]
                leastKey = key
        return leastKey
    def printCache(self):
        t = PrettyTable(['Cache Line Index','Tag',*[binary(j,self.blockOffsetBits) for j in range(2**self.blockOffsetBits)]])
        i = 0
        for key,values in self.cache.items():
            t.add_row([i,key,*values[:-1]])
            i+=1
        for i in range((2**self.cacheIndexBits)-len(self.cache)):
            t.add_row([i+len(self.cache),*['' for x in range((2**self.blockOffsetBits)+1)]])
        print(t)    
class SetAssociativeMapping:
    def __init__(self,memorySize, blockOffsetBits, cacheIndexBits, kbits,dataType):
        #chechk N is greater than other two
        self.memorySize = memorySize
        self.blockOffsetBits = blockOffsetBits
        self.cacheIndexBits = cacheIndexBits
        self.blockIndexBits = self.memorySize - blockOffsetBits
        self.kbits = kbits
        self.setIndexBits = cacheIndexBits - kbits
        self.cacheAddressBits = self.setIndexBits + blockOffsetBits
        self.tagBits = self.memorySize - self.cacheAddressBits
        self.memoryData = 'rndm' if dataType == 1 else random.randint(-2147483648,2147483647)
        self.cache = [{} for i in range(2**self.setIndexBits)]
        self.printCache()
    def write(self,address,data,other=-1):
        hitMiss = self.hitOrMiss(address)
        tag = address[0:self.tagBits]
        setIndex = address[self.tagBits:(self.tagBits+self.setIndexBits)]
        blockOffset = address[self.tagBits+self.setIndexBits:]
        #print(tag,blockIndex,blockOffset)
        setIndex = decimal(setIndex)
        blockOffset = decimal(blockOffset)
        #print(tag,blockIndex,blockOffset)
        d = self.cache[setIndex]
        if(other == -1):
            if hitMiss:
                d[tag][blockOffset] = data
                d[tag][2**self.blockOffsetBits]+=1
                print('There was a write hit and the data at the address has been updated')
            else:
                if(len(d)>=2**self.kbits):
                    prevAddress = self.findLFR(setIndex)
                    l = [self.memoryData if j!=blockOffset and j!= 2**self.blockOffsetBits else 1 if j==2**self.blockOffsetBits else data for j in range((2**self.blockOffsetBits)+1)]
                    self.cache[setIndex] = {key if key!=prevAddress else tag : value if key!=prevAddress else l for key,value in d.items()}
                    print('There was a write miss and the new tag has replaced the tag:',prevAddress,'and data of new address has been updated ')
                else:
                    d[tag] = [self.memoryData if j!=blockOffset and j!= 2**self.blockOffsetBits else 1 if j==(2**self.blockOffsetBits) else data for j in range((2**self.blockOffsetBits)+1)]
                    # d[tag][blockOffset] = data
                    print('There was a write miss and a new tag has been added to a not yet full cache and the data at the address has been updated')
        else:
            if hitMiss:
                d[tag][blockOffset] = data 
                d[tag][2**self.blockOffsetBits]+=1
                print('There was a write hit in L1 and the data at the address has been updated')
            else:
                setOther,tagOther = other.returnSet(address)
                if other.hitOrMiss(address):
                    print('write miss in L1 but hit in L2')
                    if(len(d)>=2**self.kbits):
                        prevAddress = self.findLFR(setIndex)
                        l = other.cache[setOther][tagOther]
                        self.cache[setIndex] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in d.items()}
                        d[tag][blockOffset] = data
                        other.cache[setOther][tagOther][blockOffset] = data
                        other.cache[setOther][tagOther][2**other.blockOffsetBits]+=1
                        print('the new tag has replaced the tag:',prevAddress,'in L1 and data has been updated in both')
                    else:
                        d[tag] = other.cache[setOther][tagOther]
                        d[tag][blockOffset] = data
                        other.cache[setOther][tagOther][blockOffset] = data
                        other.cache[setOther][tagOther][2**other.blockOffsetBits]+=1
                        print('new tag has been added to a not yet full L1 and data from L2 has been loaded and both are updated')
                else:
                    print('write miss in L1 and miss in L2')
                    if(len(d)>=2**other.kbits):
                        prevAddress = other.findLFR(setOther)
                        l = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache[setOther] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in other.cache[setOther].items()}
                        other.cache[setOther][tagOther][blockOffset] = data
                        print('write miss and the new tag has replaced the tag:',prevAddress,'and data has been updated in L2')
                    else:
                        other.cache[setOther][tagOther] = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache[setOther][tagOther][blockOffset] = data
                        print('There was a read miss and a new tag has been added to a not yet full L2 and data has been loaded from the memory and updated')
                    if(len(d)>=2**self.kbits):
                        prevAddress = self.findLFR(setIndex)
                        l = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        self.cache[setIndex] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in d.items()}
                        d[tag][blockOffset] = data
                        print('write miss and the new tag has replaced the tag:',prevAddress,'and data has been updated in L1')
                    else:
                        d[tag] = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        d[tag][blockOffset] = data
                        print('write miss and a new tag has been added to a not yet full L1 and data has been loaded from the memory and updated')
        self.printCache()
    def read(self,address,other=-1):
        hitMiss = self.hitOrMiss(address)
        tag = address[0:self.tagBits]
        setIndex = address[self.tagBits:(self.tagBits+self.setIndexBits)]
        blockOffset = address[self.tagBits+self.setIndexBits:]
        setIndex = decimal(setIndex)
        blockOffset = decimal(blockOffset)
        d = self.cache[setIndex]
        if(other == -1):
            if hitMiss:
                data = d[tag][blockOffset] 
                d[tag][2**self.blockOffsetBits]+=1
                print('There was a read hit and the data at the address:',address,'is',data)
            else:
                if(len(d)>=2**self.kbits):
                    prevAddress = self.findLFR(setIndex)
                    l = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    self.cache[setIndex] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in d.items()}
                    print('read miss and the new tag has replaced the tag:',prevAddress,'and data of new block has been initialized with random data ')
                else:
                    d[tag] = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                    print('There was a read miss and a new tag has been added to a not yet full cache and random data has been loaded from the memory')
        else:
            if hitMiss:
                data = d[tag][blockOffset] 
                d[tag][2**self.blockOffsetBits]+=1
                print('There was a read hit in L1 and the data at the address:',address,'is',data)
            else:
                setOther,tagOther = other.returnSet(address)
                if other.hitOrMiss(address):
                    print('read miss in L1 but hit in L2')
                    if(len(d)>=2**self.kbits):
                        prevAddress = self.findLFR(setIndex)
                        l = other.cache[setOther][tagOther]
                        self.cache[setIndex] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in d.items()}
                        print('the new tag has replaced the tag:',prevAddress)
                    else:
                        d[tag] = other.cache[setOther][tagOther]
                        print('new tag has been added to a not yet full L1 and data from L2 has been loaded')
                else:
                    print('read miss in L1 and miss in L2')
                    if(len(d)>=2**other.kbits):
                        prevAddress = other.findLFR(setOther)
                        l = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache[setOther] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in other.cache[setOther].items()}
                        other.cache[setOther][tagOther][2**other.blockOffsetBits]+=1
                        print('read miss and the new tag has replaced the tag:',prevAddress,'and data of new block has been initialized with random data in L2')
                    else:
                        other.cache[setOther][tagOther] = [1 if j==2**other.blockOffsetBits else self.memoryData for j in range((2**other.blockOffsetBits)+1)]
                        other.cache[setOther][tagOther][2**other.blockOffsetBits]+=1
                        print('There was a read miss and a new tag has been added to a not yet full L2 and random data has been loaded from the memory')
                    if(len(d)>=2**self.kbits):
                        prevAddress = self.findLFR(setIndex)
                        l = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        self.cache[setIndex] = {key if key!=prevAddress else tag :value if key!=prevAddress else l for key,value in d.items()}
                        print('read miss and the new tag has replaced the tag:',prevAddress,'and data of new block has been initialized with random data in L1')
                    else:
                        d[tag] = [1 if j==2**self.blockOffsetBits else self.memoryData for j in range((2**self.blockOffsetBits)+1)]
                        print('There was a read miss and a new tag has been added to a not yet full L1 and random data has been loaded from the memory')
        self.printCache()
    def hitOrMiss(self,address):
        tag = address[0:self.tagBits]
        setIndex = address[self.tagBits:(self.tagBits+self.setIndexBits)]
        setIndex = decimal(setIndex)
        if tag in self.cache[setIndex]:
            return True
        else:
            return False
    def findLFR(self,setIndex):
        minimum = float('inf')
        leastKey = ''
        d = self.cache[setIndex]
        for key,values in d.items():
            if(values[2**self.blockOffsetBits]<minimum):
                minimum = values[2**self.blockOffsetBits]
                leastKey = key
        return leastKey
    def printCache(self):
        t = PrettyTable(['Tag','Set Index',*[binary(j,self.blockOffsetBits) for j in range(2**self.blockOffsetBits)]])
        for i in range(2**self.setIndexBits):
            j = 0
            for key,values in self.cache[i].items():
                t.add_row([key,binary(i,self.setIndexBits),*values[:-1]])
                j+=1
            for j in range((2**self.setIndexBits)-len(self.cache[i])):
                t.add_row(['',binary(i,self.setIndexBits),*['' for x in range((2**self.blockOffsetBits))]]) 
            if(i!=(2**self.setIndexBits)-1):
                t.add_row([*['------' for x in range((2**self.blockOffsetBits)+2)]])      
        print(t)
    def returnSet(self,address):
        tag = address[0:self.tagBits]
        setIndex = address[self.tagBits:(self.tagBits+self.setIndexBits)]
        setIndex = decimal(setIndex)
        return setIndex,tag
def example():
    c = DirectMapping(7,3,2,2)
    c.write('0000010','hello,')
    c.read('0000010')
    c.read('0101011')
    c.write('0101011','world!')

    # c = AssociativeMapping(7,3,2,1)
    # c.write('0000010','hello,')
    # c.read('0000010')
    # c.read('0101011')
    # c.write('0101011','world!')
    # c.write('0110010','yes')
    # c.write('1010101','why')
    # c.write('1010101','okk')
    # c.write('1111111','damn')

    # c = SetAssociativeMapping(7,3,2,1,1)
    # c.write('0000010','hello,')
    # c.read('0000010')
    # c.read('0101011')
    # c.write('0101011','world!')
    # c.write('1010101','okk')
    # c.write('0110010','yes')
# example()
def readOrWrite(c,o = -1):
    k = int(input('Enter 1 if you want to wrote in cache, 2 if you want to read form cache and 3 If you want to return '))
    if(k==1):
        addr = input('Enter address in binary with',c.memorySize,'bits')
        if(c.dataType==1):
            data = input('Enter data you want to store ')
            while(len(data)>4):
                data = input('Size of data exceeds word size. Enter again ')
        else:
            data = int(input('Enter data you want to store '))
            while(data not in range(-2147483648,2147483647)):
                data = int(input('Size of data exceeds word size. Enter again '))
        if(o==-1):
            c.write(addr,data)
        else:
            c.write(addr,data,o)
    elif(k==2):
        addr = input('Enter address in binary with',c.memorySize,'bits')
        if(o==-1):
            c.read(addr)
        else:
            c.read(addr,o)
    elif(k==3):
        return
    else:
        print('Wrong choice entered!! Enter your choice again')
        readOrWrite(c)
def part1(other=-1):
    s = int(input('\nThe word size of machine is 32 bits or 4 bytes. Your data can either be a 4 character string or integer in range of -2147483648 to 2147483647\n Enter 1 to store characters and 2 to store integers '))
    while(s!=1 and s!=2):
        s = int(input('Wrong choice entered. Enter again '))
    if(other!=-1):
        print('Enter the following values for level 2 cache. They will be changed appropriately for level 1')
    k = int(input('\nEnter 1 for cache mapping to be direct mapping, 2 for associative mapping, and 3 for set associative mapping '))
    bs = int(input('Enter block size in powers of 2 '))
    cl = int(input('Enter number of cache lines in power of 2 '))
    n = int(input('Enter size of main memory in power of 2 '))
    flag = 0
    while(flag == 0):
        flag = 0
        if(bs>n):
            print('Main memory is not big enough to accomadate the block size. Enter all the values again')
            flag = 1
        if(cl>bs):
            print('Cache is not big enough to accomadate the block size. Enter all the values again')
            flag = 1
        if((2**cl)*(2**bs)>2**n):
            print('cache size is greater than memory. Enter all the values again')
            flag = 1
        if(flag == 1):
            bs = int(input('Enter block size in powers of 2 '))
            cl = int(input('Enter number of cache lines in power of 2 '))
            n = int(input('Enter size of main memory in power of 2 '))
    if(k==1):
        if(other == -1):
            c = DirectMapping(n,bs,cl,s)
            readOrWrite(c)
        else:
            c2 = DirectMapping(n,bs,cl,s)
            c1 = DirectMapping(n,bs,cl-1,s)
            readOrWrite(c1,c2)
    elif(k==2):
        if(other == -1):
            c = AssociativeMapping(n,bs,cl,s)
            readOrWrite(c)
        else:
            c2 = AssociativeMapping(n,bs,cl,s)
            c1 = AssociativeMapping(n,bs,cl-1,s)
            readOrWrite(c1,c2)
    else:
        while(cl>n-bs):
            print('The tag bits are coming out to be less number of sets. This might lead to duplicacy of tags in a set. Enter all the values again')
            bs = int(input('Enter block size in powers of 2 '))
            cl = int(input('Enter number of cache lines in power of 2 '))
            n = int(input('Enter size of main memory in power of 2 '))
        else:
            y = int(input('Enter K in K-ways set associative mapping or the number of cache lines in set in power of 2 '))
            while(y>cl):
                y = int(('The value of number of lines in a set is greater than the total number of lines in cache. Please enter a new value for K '))
            if(other == -1):
                c = SetAssociativeMapping(n,bs,cl,y,s)
                readOrWrite(c)
            else:
                c2 = SetAssociativeMapping(n,bs,cl,y,s)
                c1 = SetAssociativeMapping(n,bs,cl-1,y,s)
                readOrWrite(c1,c2)
    j = input('Do you want to choose a new mapping?(y/n) ')
    if(j=='y' or j =='Y'):
        part1()
    else:
        sys.exit(0)      
def taking_input():
    k = int(input('Enter 1 to query first part of assignment, 2 to query Bonus part of assignment, and 3 to exit '))
    if(k==1):
        part1()
    elif(k==2):
        part1(0)
    elif(k==3):
        sys.exit(0)
    else:
        print('Wrong choice entered!!. Enter again')
        taking_input()
taking_input()