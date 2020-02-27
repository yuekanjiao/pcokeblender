import os

#==========================================================================
def readcoke(path):    
        
    result = [] 
    numbersub = 0
    selectedsub = 0
    subnamelist = []
    subvaluelist = []
    subfrequencylist = []

    try:    
       f = open(path, 'r')    
    except:
        print("file error")
        result = []
        return result
        
    try:
        for i in range(8):
            line = f.readline()
        
        if line == '\n':
            
            numbersub = 2
            selectedsub = 0  
           
            for i in range(20):
                line = f.readline() 
            linelist = line.split(",")

            for i in range(numbersub):
                subnamelist.append(linelist[i + 1].strip())
            
            for i in range(numbersub):
                subvaluelist.append([])
                subfrequencylist.append([])
            
            line = f.readline()
            while len(line):  
                linelist = line.split(",")        
                for i in range(numbersub): 
                    subvaluelist[i].append(float(linelist[0].strip()))
                    subfrequencylist[i].append(float(linelist[i + 1].strip()))
                line = f.readline()  
            f.close() 
               
               
        elif "R'max" in line and "R'min" in line and "R'bi" in line and "anisotropy" in line:
            
            numbersub = 4
            selectedsub = 3  
            
            subnamelist.append("max")
            subnamelist.append("min")
            subnamelist.append("biref")
            subnamelist.append("anisotropy")
               
            for i in range(numbersub):
                subvaluelist.append([])
                subfrequencylist.append([])

            line = f.readline()
            while len(line):
                linelist = line.split(",")
                for i in range(numbersub):    
                    subvaluelist[i].append(float(linelist[i * 6].strip()))
                    subfrequencylist[i].append(float(linelist[i * 6 + 3].strip()))
                line = f.readline()
            f.close()
 
        else:
            
            numbersub = 2
            
            linelist = line.split(",")
            for i in range(numbersub):
                subnamelist.append(linelist[i + 1].strip())
            
            for i in range(numbersub):
                subvaluelist.append([])
                subfrequencylist.append([])
            
            line = f.readline()
            while len(line):
                linelist = line.split(",")
                for i in range(numbersub):
                    subvaluelist[i].append(float(linelist[0].strip()))
                    subfrequencylist[i].append(float(linelist[i + 1].strip()))
                line = f.readline()
            f.close()
        
        result = []
        result.append(numbersub)
        result.append(selectedsub)
        result.append(subnamelist)
        result.append(subvaluelist)  
        result.append(subfrequencylist)
    except: 
        print("file error")
        result = []
        
    return(result)

#==========================================================================
def writefit(blendpath, blendlist, cokenamelist, allcokelist, selectedsub, rangelist, volumelist, fit_frequencylist, squaredresiduals):
    dotindex = blendpath.rfind(".")
    fitpath = blendpath[:dotindex] +"_fit" +blendpath[dotindex:]    
    
    try:    
       file = open(fitpath, "w")    
    except:
        print("file error")
        return False
    
    try:
        _, tail = os.path.split(fitpath)  
        file.write(tail)
        file.write("\n\n\nSelected Range, " + str(rangelist))
        file.write("\nSquared Residuals, " + str(squaredresiduals))
        lineString = "\nvolume(%),,"
    
        listlength = len(allcokelist)
        for j in range(listlength):
            lineString = lineString + "," + str(volumelist[j])
        
        file.write(lineString)
    
        lineString = "\n\n" + str(blendlist[2][selectedsub]) + ",frequency,fit"
        for j in range(listlength):
            lineString = lineString + "," + cokenamelist[j]
        file.write(lineString)
    
        for index in range(256):
            lineString = "\n" + str(blendlist[3][selectedsub][index]) + "," + str(blendlist[4][selectedsub][index])
            lineString = lineString + "," + str(fit_frequencylist[index])
            for j in range(listlength):
                lineString = lineString + "," + str(allcokelist[j][4][selectedsub][index])
            file.write(lineString)
            

        file.close()

    except:
        print("file error")
        return False
      
    return True