import multiprocessing as mp
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import matplotlib


class ProcessPlotter(object):
    def __init__(self, z):
        self.x = []
        self.y = []
        self.z = z

    def terminate(self):
        plt.close('all')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                self.x.append(datetime.now())
                self.y.append(command)
                self.ax.plot(self.x, self.y, 'r-')
                self.ax.plot(self.x, self.y, 'ro')
                plt.draw()
        self.fig.canvas.draw()
        return True

    def move_figure(self, x, y):
        """Move figure's upper left corner to pixel (x, y)"""
        backend = matplotlib.get_backend()
        if backend == 'TkAgg':
            self.fig.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
        elif backend == 'WXAgg':
            self.fig.canvas.manager.window.SetPosition((x, y))
        else:
            # This works for QT and GTK
            # You can also use window.setGeometry
            self.fig.canvas.manager.window.move(x, y)

    def __call__(self, pipe):
        print('starting plotter...')


        fig_size = plt.rcParams["figure.figsize"]

        # Set figure width to 12 and height to 9
        fig_size[0] = 6
        fig_size[1] = 8
        plt.rcParams["figure.figsize"] = fig_size



        self.pipe = pipe
        self.fig, self.ax = plt.subplots()
        if 'RPi1' in self.z:
            self.move_figure(0, 0)
        elif 'RPi2' in self.z:
            self.move_figure(700, 0)
        self.ax.grid(True)
        plt.setp(self.ax.get_xticklabels(), rotation=45)
        self.ax.set_xlim([datetime.now(), (datetime.now()+timedelta(minutes=3))])
        self.ax.set_ylim(0, 100)
        title = str(self.z)
        self.fig.canvas.set_window_title(title)
        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()

        print('...done')
        plt.show()



class NBPlot(object):
    def __init__(self, z):
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter(z)
        self.plot_process = mp.Process(
            target=self.plotter, args=(plotter_pipe,), daemon=True)
        self.plot_process.start()

    def plot(self, data, finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        else:
            print(data)
            #data = np.random.random(2)
            send(data)

