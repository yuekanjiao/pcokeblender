import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import numpy as np  
import matplotlib.pyplot as plt
import os
import types
from blenderio import readcoke, writefit
from rngsel import RangeSelect
from blender import Blender

#==========================================================================
class BlendFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()
        self.pack()
        self.blendlist = []
        
    def plot_data(self):
        plotfigure.ax[0].cla()
        _, _, _, blend_valuelist, blend_frequencylist = self.blendlist
        subblend_valuelist = blend_valuelist[subblendframe.selected_subblend] 
        subblend_frequencylist = blend_frequencylist[subblendframe.selected_subblend]
        plotfigure.ax[0].plot(subblend_valuelist, subblend_frequencylist, 'steelblue')
        plotfigure.ax[0].relim(True)
        plotfigure.ax[0].autoscale_view(tight=True, scalex=True, scaley=True)
        # synchronize x axes of ax[0] and ax[1] - just in case
        plotfigure.ax[1].set_xlim(plotfigure.ax[0].get_xlim())    
        plt.draw()
      
    def load_data(self):
        path = fd.askopenfilename()
        if path != "":
            result = readcoke(path)
            if len(result) > 0:
                self.blendvar.set(path)
                self.blendlist = result
                subblendframe.selected_subblend = self.blendlist[1]
                subblendframe.update_subblendframe()
                self.plot_data()

    def create_widgets(self):
        self.blendbutton = tk.Button(self, text='Load Blend', command = self.load_data)
        self.blendbutton.grid(column=0,row=0) 
        self.blendvar = tk.StringVar()
        self.blendentry = ttk.Entry(self, width=68, textvariable =self.blendvar)
        self.blendentry.grid(column=1,row=0)

#==========================================================================
class SubBlendFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master) 
        self.pack()
        self.selected_subblend = -1
        self.subblendvar = tk.IntVar()
    
    def do_subblend(self):
            
        self.selected_subblend = self.subblendvar.get()
        
        # update blend plot 
        # clean ax[0] jsut in case the fit exists in it. 
        plotfigure.ax[0].cla()
        _, _, _, blend_valuelist, blend_frequencylist = blendframe.blendlist
        subblend_valuelist = blend_valuelist[self.selected_subblend] 
        subblend_frequencylist = blend_frequencylist[self.selected_subblend]
        plotfigure.ax[0].plot(subblend_valuelist, subblend_frequencylist, 'steelblue')
        plotfigure.ax[0].relim(True)
        plotfigure.ax[0].autoscale_view(tight=True, scalex=True, scaley=True)
        
        # update coke plot 
        # does not need to clean ax[1], just needs to set the data for the lines
        listboxsize = listboxframe.listbox.size()
        if listboxsize > 0 :
            if fitframe.boolrangeselect:
                xr = fitframe.rangeselect.lr.get_xdata()[0]
                xb = fitframe.rangeselect.lb.get_xdata()[0]  
                left, right = plotfigure.ax[1].get_xlim()
                rr = (xr - left) / (right - left)
                rb = (xb - left) / (right - left)
        
            # redraw all lines
            for i in range(listboxframe.listbox.size()):
                _, _, _, coke_valuelist, coke_frequencylist = cokeframe.allcokelist[i]
                subcoke_valuelist = coke_valuelist[self.selected_subblend] 
                subcoke_frequencylist = coke_frequencylist[self.selected_subblend]
                plotfigure.ax[1].lines[i].set_xdata(subcoke_valuelist)
                plotfigure.ax[1].lines[i].set_ydata(subcoke_frequencylist)
            plotfigure.ax[1].relim(True)
            plotfigure.ax[1].autoscale_view(tight=True, scalex=True, scaley=True)
            #s ynchronize x axes of ax[1] and ax[0] - just in case
            plotfigure.ax[1].set_xlim(plotfigure.ax[0].get_xlim()) 
            # redraw the selection lines
            if fitframe.boolrangeselect:
                left, right = plotfigure.ax[1].get_xlim()  
                xr = left + (right - left) * rr
                xb = left + (right - left) * rb
                fitframe.rangeselect.lr.set_xdata([xr] * 2)
                fitframe.rangeselect.lb.set_xdata([xb] * 2)
                fitframe.boolfit = True
            
        plt.draw()    
        
    def update_subblendframe(self):
        for widget in self.winfo_children():
            widget.destroy()
        number_subblend = blendframe.blendlist[0]
        subblend_namelist = blendframe.blendlist[2]   
        for i in range(number_subblend):
            (tk.Radiobutton(self, text=subblend_namelist[i], variable = self.subblendvar, value = i, command=self.do_subblend)).grid(column=i, row=0)
        self.subblendvar.set(self.selected_subblend)
        self.pack()

#==========================================================================
class CokeFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()
        self.pack()
        self.allcokelist = [] 
      
    def plot_data(self):
        listboxsize = listboxframe.listbox.size()
        if listboxsize > 0 :
            if fitframe.boolrangeselect:
                xr = fitframe.rangeselect.lr.get_xdata()[0]
                xb = fitframe.rangeselect.lb.get_xdata()[0]  
            # clear plot
            plotfigure.ax[1].cla()
            # draw all the lines in the plot
            selectedindex = listboxframe.listbox.index('active') 
            for i in range(listboxframe.listbox.size()):
                if (subblendframe.selected_subblend < 0):
                    _, selectedsub, _, coke_valuelist, coke_frequencylist = cokeframe.allcokelist[i]
                    subcoke_valuelist = coke_valuelist[selectedsub] 
                    subcoke_frequencylist = coke_frequencylist[selectedsub]
                else:
                    _, _, _, coke_valuelist, coke_frequencylist = cokeframe.allcokelist[i]
                    subcoke_valuelist = coke_valuelist[subblendframe.selected_subblend] 
                    subcoke_frequencylist = coke_frequencylist[subblendframe.selected_subblend]
                line, = plotfigure.ax[1].plot(subcoke_valuelist, subcoke_frequencylist)
                   
                if i == selectedindex:
                    line.set_color('steelblue')
                else:
                    line.set_color('dimgray')
            plotfigure.ax[1].relim(True)
            plotfigure.ax[1].autoscale_view(tight=True, scalex=True, scaley=True) 
            # redraw the selection lines
            if fitframe.boolrangeselect:  
                fitframe.rangeselect = RangeSelect(plotfigure.ax[1], xr, xb)
                fitframe.boolfit = True
            
            plt.draw()
        
    def add_plot(self): 
        path = fd.askopenfilename()
        if path != "": 
            result = readcoke(path)
            if len(result) > 0:
                self.allcokelist.append(result)
                listboxframe.listbox.selection_clear(0, 'end')
                _, tail = os.path.split(path)  
                listboxframe.listbox.insert('end', tail + ' [ 0 ≤ Volume ≤ 100 ] ' )
                # insert changes the anchor index.
                listboxframe.listbox.selection_set('end')
                listboxframe.listbox.activate('end')
                self.plot_data()
    
    def remove_plot(self):
        selectedindex = listboxframe.listbox.index('active')
        listboxsize = listboxframe.listbox.size()
        if (listboxsize > 0):
            self.allcokelist.pop(selectedindex)
            plotfigure.ax[1].lines.pop(selectedindex)
            plotfigure.ax[1].relim(True)
            plotfigure.ax[1].autoscale_view(tight=True, scalex=True, scaley=True)
            plt.draw()
    
            listboxframe.listbox.delete(selectedindex)
            if (listboxsize > 1):
                if selectedindex < (listboxsize - 1):
                    listboxframe.listbox.selection_clear(0,'end')
                    listboxframe.listbox.selection_set(selectedindex)
                    listboxframe.listbox.activate(selectedindex)
                    plotfigure.ax[1].lines[selectedindex].set_color('steelblue')
                else:
                    listboxframe.listbox.selection_clear(0,'end')
                    listboxframe.listbox.selection_set(selectedindex - 1)
                    #listboxframe.listbox.selection_anchor(selectedindex - 1)
                    listboxframe.listbox.activate(selectedindex - 1)
                    plotfigure.ax[1].lines[selectedindex - 1].set_color('steelblue')
            else:
                listboxframe.listbox.selection_clear(0,'end')

    def edit_volume(self):
        listboxsize = listboxframe.listbox.size()
        if not listboxsize > 0:
            print("\nThere is not a coke added.")
            return

        self.editroot = tk.Toplevel(root)
        
        selecteditem = listboxframe.listbox.get(listboxframe.listbox.index('active'))
        splitlist = selecteditem.split ('[')
        selectedname = splitlist[0].strip()
        nameframe = NameFrame(self.editroot)
        nameframe.namelabel.configure(text=selectedname)
        
        splitlist = splitlist[1].split(']')
        constraint = splitlist[0]
        splitlist = constraint.split("≤") 
        editframe = EditFrame(self.editroot)
        editframe.lowervar.set(splitlist[0].strip())
        editframe.uppervar.set(splitlist[2].strip())
        self.editroot.geometry('+%d+%d'%(screenwidth*2/3, screenheight/5)) 
        self.editroot.mainloop()

    def create_widgets(self):
        addbutton = tk.Button(self, text='    Add    ', command = self.add_plot)
        addbutton.grid(column=0, row=0)
        removebutton = tk.Button(self, text='    Remove    ', command = self.remove_plot)
        removebutton.grid(column=1, row=0)
        editbutton = tk.Button(self, text='    Edit    ', command = self.edit_volume)
        editbutton.grid(column=3, row=0)

#==========================================================================
class NameFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()
        self.pack()

    def create_widgets(self):
        self.namelabel = tk.Label(self, text = "CokeName")
        self.namelabel.pack()

class EditFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()
        self.pack()

    def do_ok(self):
        selectedindex = listboxframe.listbox.index('active')
        selecteditem = listboxframe.listbox.get(selectedindex)
        splitlist = selecteditem.split ('[')
        selectedname = splitlist[0].strip()
        try:
            float(self.lowervar.get().strip())
        except:
            print("invalid lower constraint")
            return
        try:
            float(self.uppervar.get().strip())
        except:
            print("invalid upper constraint")
            return    
        listboxframe.listbox.delete(selectedindex)
        listboxframe.listbox.insert(selectedindex, selectedname + ' [ '+ self.lowervar.get().strip() +' ≤ Volume ≤ '+ self.uppervar.get().strip() + ' ] ' )
        # insert changes the anchor index.
        listboxframe.listbox.selection_set(selectedindex)
        listboxframe.listbox.activate(selectedindex)
        cokeframe.editroot.destroy()

    def do_reset(self):
        self.lowervar.set("0")
        self.uppervar.set("100")

    def create_widgets(self):
        self.lowervar = tk.StringVar()
        lowerentry = ttk.Entry(self, width=10, textvar =self.lowervar)
        lowerentry.grid(column=0,row=1)

        label = tk.Label(self, text='≤ Volume ≤')
        label.grid(column=1, row=1)

        self.uppervar = tk.StringVar()
        upperentry = ttk.Entry(self, width=10, textvariable =self.uppervar)
        upperentry.grid(column=2,row=1)

        reset = tk.Button(self, text = 'Reset', command =self.do_reset)
        reset.grid(column=3, row=1)
        
        label = tk.Label(self, text='')
        label.grid(column=1, row=2)
        label = tk.Label(self, text='')
        label.grid(column=1, row=3) 

        ok = tk.Button(self, text = 'OK', command = self.do_ok)
        ok.grid(column=1, row=4)
        
        cancel = tk.Button(self, text = 'Cancel', command = cokeframe.editroot.destroy)
        cancel.grid(column=2, row=4)
       
        label = tk.Label(self, text = "")
        label.grid(column=0, row=5)

#==========================================================================
class ListBoxFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()
        self.pack()
    
    def on_select(self, evt):
        # print("on_select: ")
        # print("active index: " +str(listboxframe.listbox.index('active')))
        # print("anchor index: " +str(listboxframe.listbox.index('anchor')))
        lines = plotfigure.ax[1].lines
        # here selectedindex needs to use 'anchor'.
        # it seems 'active' was the previous activated list box item.
        selectedindex = self.listbox.index('anchor')
        for i in range(self.listbox.size()):
            line = lines[i]
            if i == selectedindex:
                line.set_color('steelblue')
            else:
                line.set_color('dimgray')
        plt.draw()
        
    def create_widgets(self):
        self.listbox = tk.Listbox(self, exportselection=False)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.configure(width=80, height=10)
        self.listbox.pack()

#==========================================================================
class FitFrame(tk.Frame):
    
    def __init__(self, master):

        super().__init__(master)
        self.create_widgets()
        self.pack()
        self.listboxsize = 0
        self.rangelist =[]
        self.fit_frequencylist = []
        self.sumerror = 0.0
        self.volumelist = []
        self.boolfit = False
        self.boolrangeselect = False

    def plot_fit(self):
        
        n = len(plotfigure.ax[0].lines)
        if n > 1:
            for i in range(1, n, 1): 
                plotfigure.ax[0].lines.pop(i)
        _, _, _, blend_valuelist, _ = blendframe.blendlist 
        subblend_valuelist = blend_valuelist[subblendframe.selected_subblend]    
        plotfigure.ax[0].plot(subblend_valuelist, self.fit_frequencylist, 'red')
        plotfigure.ax[0].relim(True)
        plotfigure.ax[0].autoscale_view(tight=True, scalex=True, scaley=True)
        plotfigure.fig.show()    
    
    def show_fit(self):
        print("===================================================")       
        print("selected range: " + str(self.get_range()))
        for listindex in range(self.listboxsize):
            listboxitem = listboxframe.listbox.get(listboxframe.listbox.index(listindex))
            splitlist = listboxitem.split ('[')
            cokename = splitlist[0].strip()
            print((cokename + ": " + "{:.2f}").format(self.volumelist[listindex]))
        print("squared residuals: " + str(self.sumerror))          
        print("===================================================")   
    
    def do_fit(self): 
        
        _, _, _, blend_valuelist, blend_frequencylist = blendframe.blendlist 
        subblend_valuelist = blend_valuelist[subblendframe.selected_subblend]
        subblend_frequencylist = blend_frequencylist[subblendframe.selected_subblend]
        
        listsize = len(subblend_valuelist)
        self.rangelist = self.get_range() 
        lowerx, upperx = self.rangelist

        index = listsize - 1
        while index > - 1 and not subblend_valuelist[index] < lowerx:
            index = index - 1
        index = index + 1    
        lowerindex = index 
        index = 0
        while index < listsize and not subblend_valuelist[index] > upperx:
            index = index + 1    
        index = index - 1
        upperindex = index
        
        indexlist = [lowerindex, upperindex]  

        self.boolfit = False
        if not len(blendframe.blendlist) > 0:
            print("There is not a blend selected.")
            return
        
        self.listboxsize = listboxframe.listbox.size()
        if not self.listboxsize > 0:
            print("There is not a coke added.")
            return
        
        lowerconstraintlist = []
        upperconstraintlist = []
        for listindex in range(self.listboxsize):
            listboxitem = listboxframe.listbox.get(listindex)
            splitlist = listboxitem.split ('[')
            splitlist = splitlist[1].split(']')
            constraint = splitlist[0]
            splitlist = constraint.split("≤") 
            lowerconstraintlist.append(float(splitlist[0].strip()))
            upperconstraintlist.append(float(splitlist[2].strip()))
        constraintlist = [lowerconstraintlist, upperconstraintlist]    
        blender = Blender(blendframe.blendlist, cokeframe.allcokelist, subblendframe.selected_subblend, constraintlist, indexlist)
        
        fitchoicevalue = self.fitchoicevar.get()
        if fitchoicevalue == 0:
            blender.qp_fit()
        else:
            blender.grid_fit(int(self.spacevar.get()))
        
        self.volumelist = blender.volumelist 
        self.fit_frequencylist = [0.0] * 256
        for listindex in range(self.listboxsize):
            _, _, _, _, coke_frequencylist = cokeframe.allcokelist[listindex]
            subcoke_frequencylist = coke_frequencylist[subblendframe.selected_subblend]       
            for k in range(256):
                self.fit_frequencylist[k] = self.fit_frequencylist[k] + self.volumelist[listindex] / 100.0 * subcoke_frequencylist[k]           
    
        self.sumerror = 0.0
        for k in range(lowerindex, upperindex + 1, 1):
            self.sumerror = self.sumerror +  (self.fit_frequencylist[k] - subblend_frequencylist[k]) ** 2

        self.plot_fit()
        self.show_fit()
        self.boolfit = True
        
    def range_select(self):
        if not self.boolrangeselect:
            self.listboxsize = listboxframe.listbox.size()
            if not self.listboxsize > 0:
                print("There is not a coke added.")
                return
            left, right = plotfigure.ax[1].get_xlim()  
            xr = left + (right - left) * 0.2
            xb = left + (right - left) * 0.8   
            self.rangeselect = RangeSelect(plotfigure.ax[1], xr, xb)
            plotfigure.fig.show()
            self.rangeselectbutton.configure(text="Full Range")
            self.boolrangeselect = True
        else:
            numberlines = len(plotfigure.ax[1].lines)
            plotfigure.ax[1].lines.pop(numberlines - 1)
            plotfigure.ax[1].lines.pop(numberlines - 2)
            plotfigure.fig.show()
            self.rangeselectbutton.configure(text="Range Select")
            self.boolrangeselect = False

    def get_range(self):
        _, _, _, blend_valuelist, _ = blendframe.blendlist 
        subblend_valuelist = blend_valuelist[subblendframe.selected_subblend]

        xmin = min(subblend_valuelist)
        xmax = max(subblend_valuelist)
        if self.boolrangeselect: 
            xr = self.rangeselect.lr.get_xdata()[0]
            xb = self.rangeselect.lb.get_xdata()[0]
            if xr < xb:
                lowerx = xr
                upperx = xb
            else:
                lowerx = xb
                upperx = xr
            if lowerx < xmin:
                lowerx = xmin
            if upperx > xmax:
                upperx = xmax        
        else:
            lowerx = xmin
            upperx = xmax
        
        return [lowerx, upperx]        
    
    def do_save(self):
        if not self.boolfit:
            print("No fit") 
            return
            
        cokenamelist = []
        for listindex in range(self.listboxsize):
            listboxitem = listboxframe.listbox.get(listboxframe.listbox.index(listindex))
            splitlist = listboxitem.split ('[')
            cokenamelist.append(splitlist[0].strip())
        
        blendpath =blendframe.blendvar.get() 
        boolsave = writefit(blendpath, 
                  blendframe.blendlist, 
                  cokenamelist, 
                  cokeframe.allcokelist,
                  subblendframe.selected_subblend,
                  self.rangelist,  
                  self.volumelist, 
                  self.fit_frequencylist,
                  self.sumerror)
        if boolsave:
            dotindex = blendpath.rfind(".")
            fitpath = blendpath[:dotindex] +"_fit" +blendpath[dotindex:]
            print("Fit has been saved as:\n" + fitpath)                         
    
    def update_fitchoice(self):
        if self.fitchoicevar.get() == 0:
            self.spaceoptions.grid_remove()
        else:
            self.spaceoptions.grid(column=4, row=0)  

    def create_widgets(self):
        tk.Label(self, text='          ').grid(column=0, row=0)
        self.fitchoicevar = tk.IntVar()
        tk.Radiobutton(self, text='Quadratic', variable = self.fitchoicevar, value = 0, command=self.update_fitchoice).grid(column=1, row=0)
        tk.Label(self, text='          ').grid(column=2, row=0)    
        tk.Radiobutton(self, text='Grid', variable = self.fitchoicevar, value = 1, command=self.update_fitchoice).grid(column=3, row=0)
        self.fitchoicevar.set(0)

        self.spacevar = tk.StringVar()
        self.spacevar.set('5')
        self.spaceoptions = tk.OptionMenu(self, self.spacevar, '10', '5','2','1')
        #self.spaceoptions.grid(column=4, row=0)    
        
        self.rangeselectbutton = tk.Button(self, text='Range Select', command = self.range_select)
        self.rangeselectbutton.grid(column=0, row=1)
        tk.Label(self, text='          ').grid(column=1, row=1)  
        tk.Button(self, text='     Fit     ', command = self.do_fit).grid(column=2, row=1)
        tk.Label(self, text='          ').grid(column=3, row=1)    
        tk.Button(self, text="     Save     ", command=self.do_save).grid(column=4, row=1)

#==========================================================================
class PlotFigure:
    
    def donotdeletewindow(self): 
        return

    def __init__(self):
        self.fig = None
        self.ax = []
        self.fig, self.ax = plt.subplots(nrows=2, ncols=1)    
        #ax[0].set_title('Histogram 1')
        #ax[0].set_ylabel('Frequency(%)')
        #ax[0].set_xlabel('Value')
        #ax[1].set_title('Histogram 2')
        #ax[1].set_ylabel('Frequency(%)')
        #ax[1].set_xlabel('Value')
        self.fig.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.15,
                    wspace=0.35)
        win = self.fig.canvas.manager.window
        win.geometry('+%d+%d'%(0,0))
        win.protocol('WM_DELETE_WINDOW', self.donotdeletewindow)
        self.fig.show()
    
#==========================================================================
def closefig():
    plt.close(plotfigure.fig)

#==========================================================================
plotfigure = PlotFigure()
plotwindow = plotfigure.fig.canvas.manager.window
root = tk.Toplevel(plotwindow)
blendframe = BlendFrame(root)
subblendframe = SubBlendFrame(root)
cokeframe = CokeFrame(root)
listboxframe = ListBoxFrame(root)
fitframe = FitFrame(root)
root.title("Coke Blender")
root.protocol('WM_DELETE_WINDOW', closefig)
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
width = plotwindow.winfo_width() 
root.geometry('+%d+%d'%(screenwidth/3, screenheight/4))  
root.mainloop()