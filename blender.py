from cvxopt import matrix, solvers

class Blender():
     
    def __init__(self, blendlist, allcokelist, selectedsub, constraintlist, indexlist):
        self.blendlist = blendlist
        self.allcokelist = allcokelist
        self.selectedsub = selectedsub
        self.lowerconstraintlist = constraintlist[0]
        self.upperconstraintlist = constraintlist[1]
        self.lowerindex = indexlist[0]
        self.upperindex = indexlist[1]
        self.listsize = len(self.allcokelist)
        self.volumelist = [0.0] * self.listsize   
    
    def qp_fit(self):
        """
        As an example, a blend f(i) is composed of 3 cokes f1(i), f2(i) and f3(i) 
        of volumes a b and c, the squared error is: 
        r = sum(a*f1 + b*f2 + c*f3 - f)^2
        = a^2*sum(f1*f1) + a*b*sum(f1*f2) + a*c*sum(f1*f3)
        + b*a*sum(f2*f1) + b^2*sum(f2*f2) + b*c*sum(f2*f3)
        + c*a*sum(f3*f1) + c*b*sum(f2*f2) + c*c*sum(f3*f3)
        - a*2*sum(f*f1) - b*2*sum(f*f2) - c*2*sum(f*f3)
        + sum(f*f)
        subject to:
        a + b + c = 1
        and 
        a ≥ 0
        b ≥ 0
        c ≥ 0
        a ≤ 100
        b ≤ 100
        c ≤ 100

        Rewrite the above in the quodratic programming standard form of CVXOPT
        P = {2*sum(f1*f1), 2*sum(f1*f2), 2*sum(f1*f3)
             2*sum(f2*f1), 2*sum(f2*f2), 2*sum(f2*f3)
             2*sum(f3*f1), 2*sum(f2*f2), 2*sum(f3*f3)}
        q = {-2*sum(f*f1))
             -2*sum(f*f2) 
             -2*sum(f*f3)}
        G = {-1
             -1
             -1
              1
              1
              1}
        h = {-0
             -0
             -0
             100
             100
             100
             }
        A = {1, 1, 1}
        b = {1}
        and igore the sum(f*f), this is a quadratic programming problem.
        r = 1/2 * X^t * P * X + q^t * X 
        """
        
        # get matrix P
        plist = []
        for i in range(self.listsize):
            _, _, _, _, coke_frequencylist = self.allcokelist[i]
            isubcoke_frequencylist = coke_frequencylist[self.selectedsub] 
            pcolumnlist=[] 
            for j in range(self.listsize):
                _, _, _, _, coke_frequencylist = self.allcokelist[j]
                jsubcoke_frequencylist = coke_frequencylist[self.selectedsub] 
                sum = 0.0
                for k in range(self.lowerindex, self.upperindex + 1, 1):
                    sum = sum + isubcoke_frequencylist[k]*jsubcoke_frequencylist[k]  
                pcolumnlist.append(2.0*sum)     
            plist.append(pcolumnlist)
        P = matrix(plist)
        
        # get matrix q
        qlist = []
        for j in range(self.listsize):
            _, _, _, _, blend_frequencylist = self.blendlist      
            subblend_frequencylist = blend_frequencylist[self.selectedsub]
            _, _, _, _, coke_frequencylist = self.allcokelist[j]
            subcoke_frequencylist = coke_frequencylist[self.selectedsub] 
            sum = 0.0
            for k in range(self.lowerindex, self.upperindex + 1, 1):
                sum = sum + subblend_frequencylist[k]*subcoke_frequencylist[k]
            qlist.append(-2.0*sum)
        q = matrix(qlist)    

        # get matrix G
        glist = []
        for i in range(self.listsize):
            gcolumnlist=[] 
            for j in range(self.listsize):
                if j == i:
                   gcolumnlist.append(-1.0) 
                else:
                   gcolumnlist.append(0.0)       
            for j in range(self.listsize):
                if j == i:
                   gcolumnlist.append(1.0) 
                else:
                   gcolumnlist.append(0.0)       
            glist.append(gcolumnlist)
        G = matrix(glist)
        
        # get matrix h
        hlist = []
        for j in range(self.listsize):
            hlist.append(-self.lowerconstraintlist[j] / 100.0)
        for j in range(self.listsize):
            hlist.append(self.upperconstraintlist[j] / 100.0)
        h = matrix(hlist)
        
        # get matrix A
        alist = []
        for i in range(self.listsize):  
            alist.append(1.0)
        A = matrix(alist, (1, self.listsize))
        
        # get matrix b
        b=matrix(1.0)

        sol=solvers.qp(P, q, G, h, A, b)
        #print(self.sol['x'])
        
        self.volumelist = [0.0] * self.listsize
        for listindex in range(self.listsize):
            self.volumelist[listindex] = sol['x'][listindex] * 100.0
       
    def grid_fit(self, volumegridspace):
        
        self.volumegridlist = []
        for i in range(self.listsize):
            volumerowlist = range(int(self.lowerconstraintlist[i]), int(self.upperconstraintlist[i]) + volumegridspace, volumegridspace)
            self.volumegridlist.append(volumerowlist)

        listindex = -1
        self.currentvolumelist = [0.0] * self.listsize
        self.sumerror = float("inf")
        self.iterate_grid(listindex)

    def iterate_grid(self, listindex):
        
        listindex = listindex + 1
        
        sumvolume = 0.0
        for volumeindex in range(listindex):
            sumvolume = sumvolume + self.currentvolumelist[volumeindex]
        # In case of listIndex = 0, sumVolume = 0 
        volumerowlist = self.volumegridlist[listindex]
        volumerowlength = len(volumerowlist)

        if listindex < (self.listsize - 1):
            columnindex = 0
            while columnindex < volumerowlength and not((sumvolume + volumerowlist[columnindex]) > 100):
                self.currentvolumelist[listindex] = volumerowlist[columnindex]
                self.iterate_grid(listindex)
                columnindex = columnindex + 1
        else:
            """
            listIndex = listColunt - 1  
            Only check the error sum for volume sum = 100,
             A speical case - listCount = 1:
             listIndex = 0 and listIndex < (listCount - 1) is false,
             iterating comes here directly and for loop does not run,
             therefore volumeCurrentArray[listIndex] = 100. 
            """
            columnindex = 0
            while columnindex < volumerowlength and (sumvolume + volumerowlist[columnindex]) < 100:
                columnindex = columnindex + 1
            
            # Did not find a columnIndex value where all volumes make up reaches 100.
            if columnindex > (volumerowlength - 1):
                return 
            
            self.currentvolumelist[listindex] = volumerowlist[columnindex]
            self.fit_frequencylist = [0 for i in range(256)] 
            for listindex in range(self.listsize):
                _, _, _, _, coke_frequencylist = self.allcokelist[listindex]
                subcoke_frequencylist = coke_frequencylist[self.selectedsub]       
                for k in range(self.lowerindex, self.upperindex + 1, 1):
                    self.fit_frequencylist[k] = self.fit_frequencylist[k] + self.currentvolumelist[listindex] / 100.0 * subcoke_frequencylist[k]           
            
            _, _, _, _, blend_frequencylist = self.blendlist      
            subblend_frequencylist = blend_frequencylist[self.selectedsub]
            newsumerror = 0.0
            for k in range(self.lowerindex, self.upperindex + 1, 1):
                newsumerror = newsumerror +  (self.fit_frequencylist[k] - subblend_frequencylist[k]) ** 2
            if newsumerror < self.sumerror:
                for volumeindex in range(self.listsize):
                    self.volumelist[volumeindex] = self.currentvolumelist[volumeindex]
                self.sumerror = newsumerror    
                print(str(self.volumelist) + "    " + str(self.sumerror))
 