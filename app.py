import sys, csv, os
from datetime import datetime as dt
from my_lib import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg

session_info = []
class SessionInfo:
    pass
session = SessionInfo()
session.id = 1
cpu_info = []
class CPUInfo:
    pass
cpu = CPUInfo()
mem_info = []
class MemInfo:
    pass
mem = MemInfo()
disks_info = []
class DisksInfo:
    pass
storage = DisksInfo()

def get_session_id():
    filename = 'csv/sessions.csv'
    if os.path.isfile(filename):
        with open(filename) as file:
            readCSV = list(csv.reader(file, delimiter=','))
            session.id = int(len(readCSV))
            
def write_session_info():
    session_info.append({
        'id' : session.id,
        'session_start' : session.session_start,
        'session_end' : session.session_end,
        'ip' : session.ip,
        'community' : session.community
        })
    
    filename = 'csv/sessions.csv'
    flag = 'w'
    if os.path.isfile(filename):
        flag = 'a'
    with open(filename, flag, newline='') as file:
        columns = ['id', 'session_start', 'session_end', 'ip', 'community']
        writer = csv.DictWriter(file, fieldnames=columns)
        if (flag == 'w'):
            writer.writeheader()
        
        writer.writerows(session_info)
        file.close()

def write_cpu_info():
    filename = 'csv/cpu_usage.csv'
    flag = 'w'
    if os.path.isfile(filename):
        flag = 'a'
    with open(filename, flag, newline='') as file:
        columns = ['session_id', 'usage', 'processes', 'sys_up_time', 'timestamp']
        writer = csv.DictWriter(file, fieldnames=columns)
        if (flag == 'w'):
            writer.writeheader()
        
        writer.writerows(cpu_info)
        file.close()

def write_mem_info():
    filename = 'csv/mem_usage.csv'
    flag = 'w'
    if os.path.isfile(filename):
        flag = 'a'
    with open(filename, flag, newline='') as file:
        columns = ['session_id', 'virt_used', 'virt_size', 'phys_used', 'phys_size', 'timestamp']
        writer = csv.DictWriter(file, fieldnames=columns)
        if (flag == 'w'):
            writer.writeheader()
        
        writer.writerows(mem_info)
        file.close()

def write_disks_info():
    filename = 'csv/disks_usage.csv'
    flag = 'w'
    if os.path.isfile(filename):
        flag = 'a'
    with open(filename, flag, newline='') as file:
        columns = ['session_id', 'description', 'used_space', 'size', 'timestamp']
        writer = csv.DictWriter(file, fieldnames=columns)
        if (flag == 'w'):
            writer.writeheader()
        
        writer.writerows(disks_info)
        file.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setStyleSheet(
        #     'QMainWindow { background-color: #F3E8EE; }'
        #     'QLabel { color: #050517; font: bold 15px; margin: 5px 13px; }'
        #     'QLineEdit { border: 2px solid gray; border-radius: 5px; font: 13px; padding: 5px; margin: 0px 10px; }'
        #     'QPushButton { background-color: #050517; color: #F3E8EE; font: bold 15px; border-radius: 5px; padding: 5px; margin: 15px 10px;}'
        # )
        self.setWindowTitle('кого мониторим?')

        layout = QVBoxLayout()
        self.widgets = [
            QLabel('введите ip4:'),
            QLineEdit(),
            QLabel('введите название сообщества:'),
            QLineEdit(),
            QPushButton('применить')
        ]

        for w in self.widgets:
            layout.addWidget(w)

        widget = QWidget()
        widget.setLayout(layout)

        # self.widgets[1].setInputMask('000.000.000.000;_')
        self.widgets[4].clicked.connect(self.start_monitoring)

        self.setCentralWidget(widget)
    
    def start_monitoring(self):
        get_session_id()
        session.session_start = dt.now()
        # session.session_start = now.strftime('%d.%m.%Y, %H:%M:%S')

        ip = self.widgets[1].text()
        str = self.widgets[3].text()
        session.ip = ip
        session.community = str
        self.w = MonitorWindow(str, ip)
        self.close()
        # self.w.show()
        # self.w.start_timer()

class MonitorWindow(QWidget):
    def __init__(self, str, ip):
        super().__init__()
        self.setStyleSheet('QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #7DDF64; }')
        self.setWindowTitle('диспетчер задач 2.0')

        self.str = str
        self.ip = ip

        layout = QVBoxLayout()
        self.label = QLabel()
        self.processes = QLabel()
        self.sys_up_time = QLabel()
        self.phys_mem = QLabel()
        self.virt_mem = QLabel()
        self.timer = QTimer()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle('ЦП')
        self.plot_widget.setLabel('left', 'использование (%)')
        self.plot_widget.setLabel('bottom', 'время (с)')

        self.plot_widget1 = pg.PlotWidget()
        self.plot_widget1.setTitle('Память')
        self.plot_widget1.setLabel('left', 'использование (%)')
        self.plot_widget1.setLabel('bottom', 'время (с)')

        l = QVBoxLayout()
        l2 = QVBoxLayout()
        # w = QWidget()
        # l.addWidget(w)
        # w.setMinimumSize(500, 300)
        # ll = QVBoxLayout()
        # w.setLayout(ll)
        l.addWidget(self.plot_widget)
        l2.addWidget(self.plot_widget1)

        # hbox = QHBoxLayout()
        grid_layout = QGridLayout()
        grid_layout1 = QGridLayout()
        
        cpu_lbl = QLabel()
        processes_lbl = QLabel()
        time_lbl = QLabel()
        cpu_lbl.setText('Использование')
        processes_lbl.setText('Процессы')
        time_lbl.setText('Время работы')
        grid_layout.addWidget(cpu_lbl, 0, 0)
        grid_layout.addWidget(processes_lbl, 0, 1)
        grid_layout.addWidget(time_lbl, 0, 2)
        grid_layout.addWidget(self.label, 1, 0)
        grid_layout.addWidget(self.processes, 1, 1)
        grid_layout.addWidget(self.sys_up_time, 1, 2)
        grid_layout.setContentsMargins(20, 10, 20, 10)

        phys_lbl = QLabel()
        virt_lbl = QLabel()
        phys_lbl.setText('Физическая память')
        virt_lbl.setText('Виртуальная память')
        grid_layout1.addWidget(phys_lbl, 0, 0)
        grid_layout1.addWidget(virt_lbl, 0, 1)
        grid_layout1.addWidget(self.phys_mem, 1, 0)
        grid_layout1.addWidget(self.virt_mem, 1, 1)
        grid_layout1.setContentsMargins(20, 10, 20, 10)

        # hbox.addWidget(self.label)
        # hbox.addWidget(self.processes)
        # hbox.addWidget(self.sys_up_time)
        tab_widget = QTabWidget()
        self.update_disks = QPushButton('обновить')
        
        w = QWidget()
        w2 = QWidget()
        w3 = QWidget()
        ll = QVBoxLayout()
        ll2 = QVBoxLayout()
        self.ll3 = QVBoxLayout()
        self.ll3.addWidget(self.update_disks)
        ll.addLayout(l)
        ll2.addLayout(l2)
        ll.addLayout(grid_layout)
        ll2.addLayout(grid_layout1)
        w.setLayout(ll)
        w2.setLayout(ll2)
        w3.setLayout(self.ll3)

        tab_widget.addTab(w, 'ЦП')
        tab_widget.addTab(w2, 'Память')
        tab_widget.addTab(w3, 'Диски')
        layout.addWidget(tab_widget)
        # layout.addLayout(l)
        # layout.addLayout(grid_layout)
        self.setLayout(layout)

        self.x = [0]
        self.y = [0]
        self.x1 = [0]
        self.y1 = [0]
        # self.plot_widget.setLimits(xMin = 0, yMin = 0)
        self.plot_widget.setYRange(0,100)
        self.plot_widget.setGeometry(0, 0, 60, 100)
        self.plot_curve = self.plot_widget.plot()
        self.plot_widget1.setYRange(0,100)
        self.plot_widget1.setGeometry(0, 0, 60, 100)
        self.plot_curve1 = self.plot_widget1.plot()
        
        self.timer.timeout.connect(self.show_cpu_usage)
        self.timer.timeout.connect(self.show_mem_usage)
        self.timer.timeout.connect(self.update_plot)
        self.timer.timeout.connect(self.update_plot1)
        self.update_disks.clicked.connect(self.show_disks)
        self.start_timer()
        self.show()
        self.show_disks()
    
    def closeEvent(self, event):
        self.timer.stop()
        session.session_end = dt.now()
        # session.session_end = now.strftime('%d.%m.%Y, %H:%M:%S')
        write_session_info()
        write_cpu_info()
        write_mem_info()
        write_disks_info()
        # print('остановили таймер')
        pass

    def start_timer(self):
        self.timer.start(2000)

    def show_disks(self):
        if (self.ll3.count() > 1):
            self.ll3.itemAt(1).widget().setParent(None)
        wdt = QWidget()
        self.ll3.addWidget(wdt)
        l33 = QVBoxLayout()
        wdt.setLayout(l33)
        disks = get_storage_info(self.str, self.ip)[:-2]
        key = 0
        for disk in disks:
            storage.desc = str(disk.desc)[:9]
            storage.used = disk.used
            storage.size = disk.size
            storage.time = dt.now()
            # session.session_end = now.strftime('%d.%m.%Y, %H:%M:%S')
            disks_info.append({
                'session_id' : session.id,
                'description' : storage.desc,
                'used_space' : storage.used,
                'size' : storage.size,
                'timestamp' : storage.time
                })
            desc = disk.desc
            used = disk.used
            size = disk.size
            # label1 = QLabel()
            # l33.addWidget(label1, key)
            l33.addWidget(QLabel(str(desc)))
            # label1.setText(str(desc))
            pg = QProgressBar()
            l33.addWidget(pg, key)
            pg.setRange(0, int(size))
            pg.setValue(int(used))
            # label2 = QLabel()
            # l33.addWidget(label2, key)
            # label2.setText('Использовано ' + str(used) + ' ГБ из ' + str(size) + ' ГБ.')
            l33.addWidget(QLabel('Использовано ' + str(used) + ' ГБ из ' + str(size) + ' ГБ.'))
            key += 1
        
    def show_cpu_usage(self):
        text = calc_cpu_usage(self.str, self.ip)
        self.label.setText(str(text) + '%')
        cpu.usage = str(text) + '%'
        text = get_processes(self.str, self.ip)
        self.processes.setText(str(text))
        cpu.processes = str(text)
        text = get_sys_up_time(self.str, self.ip)
        self.sys_up_time.setText(str(text))
        cpu.sys_up_time = str(text)
        cpu.time = dt.now()
        cpu_info.append({
            'session_id' : session.id,
            'usage' : cpu.usage,
            'processes' : cpu.processes,
            'sys_up_time' : cpu.sys_up_time,
            'timestamp' : cpu.time
        })
    
    def show_mem_usage(self):
        text = get_storage_info(self.str, self.ip)[-2:]
        self.phys_mem.setText(str(text[1].used) + ' ГБ / '+ str(text[1].size) + ' ГБ')
        self.virt_mem.setText(str(text[0].used) + ' ГБ / '+ str(text[0].size) + ' ГБ')
        mem.virt_used = str(text[0].used)
        mem.virt_size = str(text[0].size)
        mem.phys_used = str(text[1].used)
        mem.phys_size = str(text[1].size)
        mem.time = dt.now()
        mem_info.append({
            'session_id' : session.id,
            'virt_used' : mem.virt_used,
            'virt_size' : mem.virt_size,
            'phys_used' : mem.phys_used,
            'phys_size' : mem.phys_size,
            'timestamp' : mem.time
        })
    
    def update_plot(self):
        y = calc_cpu_usage(self.str, self.ip)
        if (len(self.x) == 60):
            self.x = self.x[1:]  # Remove the first x element.
            self.y = self.y[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        elif (len(self.x) == 0):
            self.x.append(0)
        else:
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        
        self.y.append(y)

        # print(str(self.x[-1]) + '; ' + str(y))
        self.plot_curve.setData(self.x, self.y)
    
    def update_plot1(self):
        y = round((float(get_storage_info(self.str, self.ip)[-2:][1].used) / float(get_storage_info(self.str, self.ip)[-2:][1].size)) * 100)
        # print(y)
        if (len(self.x1) == 60):
            self.x1 = self.x1[1:]  # Remove the first x element.
            self.y1 = self.y1[1:]  # Remove the first y element.
            self.x1.append(self.x1[-1] + 1)  # Add a new value 1 higher than the last.
        elif (len(self.x1) == 0):
            self.x1.append(0)
        else:
            self.x1.append(self.x1[-1] + 1)  # Add a new value 1 higher than the last.
        
        self.y1.append(y)

        # print(str(self.x1[-1]) + '; ' + str(y))
        self.plot_curve1.setData(self.x1, self.y1)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

# app.exec()
sys.exit(app.exec())