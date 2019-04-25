import sys,socket,os,re,threading,time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from filetrans import *
import hashlib


class Mymainwindow(QMainWindow,Ui_Form):
    singal1 = pyqtSignal(str)  # 自定义一个文本框输出信号
    singal2 = pyqtSignal(float,float)  # 自定义一个浮点类型的发送速度信息的信号
    



    def __init__(self,partent=None):
        super(Mymainwindow,self).__init__(partent)
        self.setupUi(self)
        self.params_dic = {'ip':'null','filename':'null','speed':'0'}
        self.status = self.statusBar()
        self.status.showMessage(
            "当前传输的文件: {},  当前传输IP: {},  当前网速: {}MB/s".format(self.params_dic["filename"],
                                                             self.params_dic["ip"],
                                                             self.params_dic["speed"]))

    def checkmd5(self):
        try:
            md5_ = hashlib.md5()
            n = 100  # 检查前100*2048md5
            with open("copy_{}".format(self.params_dic["filename"]),"rb") as p:

                while n:
                    data = p.read(2048)
                    if not data:
                        break
                    md5_.update(data)
                    n -= 1
                print(str(md5_.hexdigest()))
                print(self.md5)
            if md5_.hexdigest()==self.md5:
                self.textBrowser.append("快速md5值均为：%s"%self.md5)
        except:
            self.textBrowser.append("校验失败,请确保已完成文件传输")


    def md5_check(self,filename): # 校验MD5

        md5_ = hashlib.md5()
        n=100 # 检查前100*2048 md5
        with open(filename, "rb") as p:
            while n:

                data = p.read(2048)
                if not data:
                    break
                md5_.update(data)
                n-=1
        print(md5_.hexdigest())
        self.md5 = md5_.hexdigest()



    def switch(self, params):

        if params == "up":
            '''---    ---'''
            self.get_params("filename", self.lineEdit_2.text())
            self.get_params("ip", self.lineEdit.text())
            self.textBrowser.append("UP_MODE")  # 输出日志
            self.widget = Mymainwindow()  # IMP
            self.widget.singal1[str].connect(self.textchange)
            sign=1
            self.thread1(sign)
            sign -= 1

        if params == "down":
            self.textBrowser.append("DOWN_MODE")
            self.widget = Mymainwindow()  # IMP
            ip = self.get_realip()
            self.textBrowser.append("本机ip:{}".format(ip))
            self.widget.singal1[str].connect(self.textchange)
            sign=1
            self.thread2(sign)
            sign-=1

    def thread1(self,sign):#up_mode
        a = threading.Thread(target=self.client,args=(sign,self.params_dic["ip"],self.params_dic["filename"],))  # target=self.client,args=(ip,filename,)
        a.start()
        print("线程a开启")




    def thread2(self,sign):
        b = threading.Thread(target=self.server,args=(sign,))
        print("线程2开启")
        b.start()


    def showspeed(self,speed,filesize):

        self.params_dic["speed"] = round(speed,1)
        self.params_dic["filesize"] = round(filesize,1)
        self.status.showMessage(
            "当前传输数据大小{}MB,当前网速:{}MB/s".format(self.params_dic["filesize"],self.params_dic["speed"]))

    def get_params(self, type, params):

        self.params_dic[type] = params
        print(self.params_dic)

    def textchange(self,num):
        self.textBrowser.append(num)


    def get_realip(self):
        filename = "ip.swbd"
        # open(filename, "w").write("")
        os.system("ipconfig > {}".format(filename))
        text = open("{}".format(filename)).read()
        # print(text)
        try:
            ipv4 = re.findall(r'以太网适配器 以太网:(.*?)默认网关', text, re.S)[0]
            ipv4 = re.findall(r'IPv4 地址 . . . . . . . . . . . . :(.*?)子网掩码', ipv4, re.S)[0].replace(" ", "")
            print(ipv4)
        except:
            ipv4 = re.findall(r'无线局域网适配器 WLAN:(.*?)默认网关', text, re.S)[0]
            ipv4 = re.findall(r'IPv4 地址 . . . . . . . . . . . . :(.*?)子网掩码', ipv4, re.S)[0].replace(" ", "")
            print(ipv4)
        os.remove(filename)
        return ipv4


    def client(self,sign,ip, filename):
        th1 = threading.Thread(target=self.md5_check,args=(self.params_dic["filename"],))
        th1.start()
        time.sleep(0.1)
        print("md5校验线程开启")
        print(self.md5)
        IP_Port = (ip, 8896)
        sk = socket.socket()
        sk.connect(IP_Port)  # 连接目标地址
        while sign:

            size = os.stat(filename).st_size  # 读取文件大小
            file_info = 'post|%s|%s|%s' % (filename,size,self.md5)  # 发送数据的属性
            print(file_info)
            sk.sendall(bytes(file_info, "utf-8"))
            print("正在等待0.1S")
            time.sleep(0.1)
            has_sent = 0
            with open(filename, 'rb') as p:

                fre = 0

                while has_sent != size:
                    n=1024 # 传输完成1MB数据
                    time0 = time.time()
                    while n:
                        n-=1
                        data = p.read(1024)  # 1KB
                        sk.sendall(data)
                        has_sent += len(data)

                        num = int(100 * has_sent / size)
                        num = "%d"%num
                        if fre!=num:
                            self.widget.singal1.emit("当前上传进度:{}%    ".format(num))         # 发射信号

                        fre = num
                    speed = 1/(time.time()-time0)


                    filesize = has_sent/(1024**2)

                    print("当前传输数据总量{}".format(filesize))
                    self.params_dic['speed']=speed
                    self.widget.singal2.emit(speed,filesize)  # 发射速度和文件大小信号
                    self.widget.singal2[float,float].connect(self.showspeed)  # 连接信号



            print('\n上传成功')

            sign -= 1





    def server(self,sign):
        print("Working...")
        ip_port = ("0.0.0.0", 8896)  # 远程ip,设置端口号为8896
        sk = socket.socket()
        sk.bind(ip_port)  # 设置地址
        sk.listen(5)  # 服务器能够接受的连接数

        while sign:
            connect, address = sk.accept()
            print("%s已连接" % connect)
            while sign:

                # 取得数据包大小

                data = connect.recv(1024)
                time.sleep(0.5)

                if str(data).replace("b'", "").replace("'", "") == "":

                    pass

                else:

                    # data = str(data).replace("b'","").replace("'","")
                    # cmd,file,size = re.findall(r'(.*?)\|(.*?)\|(\d+)',data)[0]  # 防止乱码
                    data1 = re.findall(r'b\'(.*?)\'',str(data))[0]
                    cmd, file, size, md5 = data1.split("|")
                    self.params_dic["filename"] = file
                    self.md5 = md5
                    print(md5)
                    # data = str(data).replace("b'", "").replace("'", "")
                    # cmd, file, size = re.findall(r'(.*?)\|(.*?)\|(\d+)', data)[0]  # 防止乱码
                    size = int(size)
                    has_sent = 0  # 当前接收大小
                    time.sleep(0.1)
                    with open("copy_" + file, "wb") as p:
                        fre1 = 0
                        while has_sent != size:
                            MBytes = 1024
                            time0 = time.time()
                            while MBytes:

                                MBytes-=1
                                data = connect.recv(1024)
                                p.write(data)
                                has_sent += len(data)
                                # sys.stdout.write(
                                #     "\r[%s] %d%%" % ('|' * int((has_sent / size) * 100), int(100 * has_sent / size))) #
                                # sys.stdout.flush()
                                num = int(100    * has_sent / size)
                                num = "%d" % num

                                if fre1 != num:
                                    self.widget.singal1.emit("当前下载进度:{}%".format(num))  # 发射信号

                                fre1 = num
                            speed = 1/(time.time()-time0)
                            self.params_dic['speed'] = speed
                            self.widget.singal2.emit(speed,float(size/1024**2))  # 发射速度信号
                            self.widget.singal2[float,float].connect(self.showspeed)  # 连接信号

                    # time.sleep(1)
                    # data = connect.recv(1024)
                    # print(str(data))
                    print("\n%s保存成功" % file)
                    print(md5)

                    sign -= 1




if __name__ == '__main__':

    app = QApplication(sys.argv)
    myWin = Mymainwindow()
    myWin.show()
    sys.exit(app.exec_())
