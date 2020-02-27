import matplotlib.pyplot as plt

class RangeSelect():
            
    def getline(self, event):
        #print(event.xdata)
        #print(self.lr.get_xdata())
        #print(self.lb.get_xdata())
        if event.xdata == None:
            return False   
        if abs(event.xdata - self.lr.get_xdata()[0]) < abs((self.right - self.left) * 0.01):
            self.line = 1
        elif abs(event.xdata - self.lb.get_xdata()[0]) < abs((self.right - self.left) * 0.01):
            self.line = 2
        return True

    def button_pressed(self, event):
        if not self.getline(event):
            return
        #print("pressed")
        self.boolpressed = True
        if self.line == 1:
            self.lr.set_xdata([event.xdata] * 2)
        elif self.line == 2:
            self.lb.set_xdata([event.xdata] * 2)
        plt.draw()

    def button_released(self, event):
        #print("relased")
        self.boolpressed = False

    def button_dragged(self, event):
        if not self.getline(event):
            return
        if self.boolpressed:
            #print("dragged") 
            if self.line == 1:
                self.lr.set_xdata([event.xdata] * 2)
            elif self.line == 2:
                self.lb.set_xdata([event.xdata] * 2)
            plt.draw()

    def __init__(self, ax, xr, xb):
        self.left, self.right = ax.get_xlim()  
        self.lr = ax.axvline(x=xr, color='r')
        self.lb = ax.axvline(x=xb, color='b')
        self.line = 1
        self.boolpressed = False
        plt.connect('button_press_event', self.button_pressed)
        plt.connect('button_release_event', self.button_released)
        plt.connect('motion_notify_event', self.button_dragged)
        #plt.draw()
   