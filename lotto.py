from itertools import count
from PyQt5.QtWidgets import QMainWindow
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import models
from time import sleep
import requests
from bs4 import BeautifulSoup
import datetime as dt
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from lottoUI_3 import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import webbrowser


class lottoProcess(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.lottoPhotos=[self.lottoPhoto,self.lottoPhoto_2,self.lottoPhoto_3,self.lottoPhoto_4,self.lottoPhoto_5,self.lottoPhoto_6,self.lottoPhoto_7,self.lottoPhoto_8
            ,self.lottoPhoto_9,self.lottoPhoto_10,self.lottoPhoto_11,self.lottoPhoto_12,self.lottoPhoto_13,self.lottoPhoto_14,self.lottoPhoto_15,self.lottoPhoto_16,
            self.lottoPhoto_17,self.lottoPhoto_18,self.lottoPhoto_20,self.lottoPhoto_24,self.lottoPhoto_19,self.lottoPhoto_23,self.lottoPhoto_21,self.lottoPhoto_22,
            self.lottoPhoto_26,self.lottoPhoto_30,self.lottoPhoto_25,self.lottoPhoto_29,self.lottoPhoto_27,self.lottoPhoto_28,self.lottoPhoto_32,self.lottoPhoto_36,
            self.lottoPhoto_31,self.lottoPhoto_35,self.lottoPhoto_33,self.lottoPhoto_34,self.lottoPhoto_39,self.lottoPhoto_37,self.lottoPhoto_41,self.lottoPhoto_40,
            self.lottoPhoto_38,self.lottoPhoto_42,self.lottoPhoto_44,self.lottoPhoto_43,self.lottoPhoto_45,self.lottoPhoto_46,self.lottoPhoto_47,self.lottoPhoto_48,
            self.lottoPhoto_50,self.lottoPhoto_49,self.lottoPhoto_52,self.lottoPhoto_54,self.lottoPhoto_53,self.lottoPhoto_51,self.lottoPhoto_55,self.lottoPhoto_59,
            self.lottoPhoto_60,self.lottoPhoto_56,self.lottoPhoto_58,self.lottoPhoto_57]  
        self.recommends = [self.recommend,self.recommend_2,self.recommend_3,self.recommend_4,self.recommend_5,self.recommend_6,self.recommend_7,self.recommend_8,
        self.recommend_9,self.recommend_10]

    def numbers2ohbin(self,numbers):

        self.ohbin = np.zeros(45) #45개의 빈 칸을 만듬

        for i in range(6): #여섯개의 당첨번호에 대해서 반복함
            self.ohbin[int(numbers[i])-1] = 1 #로또번호가 1부터 시작하지만 벡터의 인덱스 시작은 0부터 시작하므로 1을 뺌
        
        return self.ohbin

    # 원핫인코딩벡터(ohbin)를 번호로 변환
    def ohbin2numbers(self,ohbin):

        self.numbers = []
        for i in range(len(self.ohbin)):
            if self.ohbin[i] == 1.0: # 1.0으로 설정되어 있으면 해당 번호를 반환값에 추가한다.
                self.numbers.append(i+1)
        
        return self.numbers
    def get_bestNum(self, nums_prob):
        self.ball_box=[]
        nums_prob = nums_prob.tolist()
        for i in range(6):
            maxNum = nums_prob.index(max(nums_prob))
            nums_prob[maxNum] = -1
            self.ball_box.append(maxNum+1)
        return self.ball_box
    def gen_numbers_from_probability(self,nums_prob): #확률 값을 받고 표시하기

        self.ball_box = []

        for n in range(45):
            self.ball_count = int(nums_prob[n] * 100 + 1)
            self.ball = np.full((self.ball_count), n+1) #1부터 시작
            self.ball_box += list(self.ball)

        self.selected_balls = []

        while True:
            
            if len(self.selected_balls) == 6:
                break
            
            self.ball_index = np.random.randint(len(self.ball_box), size=1)[0]
            self.ball = self.ball_box[self.ball_index]

            if self.ball not in self.selected_balls:
                self.selected_balls.append(self.ball)

        return self.selected_balls

    def dialog_open(self):
        self.dialog = QDialog()    
        self.dialog.setWindowTitle('Dialog')
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(400, 300)
        self.gotolotto = QtWidgets.QPushButton(self.dialog)
        self.gotolotto.setGeometry(QtCore.QRect(100,200,200,100))
        self.gotolotto.setStyleSheet("background-image:url(./photo/gotolotto.png);")
        self.gotolotto.clicked.connect(self.openLotto)
        self.noticelabel = QtWidgets.QLabel(self.dialog)
        self.noticelabel.setObjectName("noticelabel")
        self.noticelabel.setGeometry(QtCore.QRect(0,0,400,200))
        self.noticelabel.setPixmap(QtGui.QPixmap("./photo/help.png"))
        self.dialog.show()
    def openLotto(self):
        webbrowser.open("https://dhlottery.co.kr/gameInfo.do?method=buyLotto&wiselog=C_A_1_3")    

    def process(self):
        for i in self.lottoPhotos:
            i.clear()
        for l in self.recommends:
            l.clear()    
        self.numberList = []
        self.baseURL = 'https://superkts.com/lotto/list/?pg='
        self.progressBar.setProperty("value", 5)  
        for i in range(100):
            try:
                self.r = requests.get(url=self.baseURL+str(i))
                self.soup = BeautifulSoup(self.r.content, "lxml")
                self.table = self.soup.findAll('td',{'class':'no'})
                for j in self.table:   
                    j = j.get_text(' ')
                    self.spl_table = j.split() 
                    self.numberList.append(self.spl_table[:6])
            except:
                pass        

        self.lottoNumbers = []
        for i in self.numberList:
            self.lottoNumbers.append(list(map(int, i)))

        self.progressBar.setProperty("value", 40)
        self.ohbins = list(map(self.numbers2ohbin, self.lottoNumbers)) # 원-핫 인코딩하기
        self.train_idx = (0,800)
        self.val_idx = (801,900)
        self.test_idx = (900,len(self.lottoNumbers))

        self.model = keras.Sequential([
        keras.layers.LSTM(128, batch_input_shape=(1, 1, 45), return_sequences=False, stateful=True),
        keras.layers.Dense(45, activation='sigmoid')
        ])
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])   
        self.x_samples = self.ohbins[0:len(self.ohbins)-1]
        self.y_samples = self.ohbins[1:len(self.ohbins)] 
        self.batch_train_loss = []
        self.batch_train_acc = []
        self.train_loss = []
        self.train_acc = []
        self.val_loss = []
        self.val_acc = []
        import os
        if os.path.exists('./base_model/saved_model.pb'):
            self.model= models.load_model("./base_model/")
        self.progressBar.setProperty("value", 60)
        for epoch in range(1):

            self.model.reset_states() # 중요! 매 에포크마다 1회부터 다시 훈련하므로 상태 초기화 필요

            for i in range(len(self.x_samples)):
            
                self.xs = self.x_samples[i].reshape(1, 1, 45)
                self.ys = self.y_samples[i].reshape(1, 45)
                
                loss, acc = self.model.train_on_batch(self.xs, self.ys) 
                # #배치만큼 모델에 학습시킴
                # loss, acc = model.fit(xs,ys)
                self.batch_train_loss.append(loss)
                self.batch_train_acc.append(acc)

            self.train_loss.append(np.mean(self.batch_train_loss))
            self.train_acc.append(np.mean(self.batch_train_acc))

            # print('epoch {0:4d} train acc {1:0.3f} loss {2:0.3f}'.format(epoch, np.mean(self.batch_train_acc), np.mean(self.batch_train_loss)))
            # model.save('./lotto_model/model'+str(dt.date.today()))
        self.progressBar.setProperty("value", 90)
        self.model.save("base_model")        
        self.xs = self.x_samples[-1].reshape(1, 1, 45)
        self.ys_pred = self.model.predict_on_batch(self.xs)
        self.list_numbers = [] # 결과 값
        self.count = 0
        if self.comboBox.currentIndex() <= 3 : self.count = 24
        for n in range(self.comboBox.currentIndex()+1):
            if self.comboBox.currentIndex()==0:
                self.numbers = self.get_bestNum(self.ys_pred[0])
            else:
                self.numbers = self.gen_numbers_from_probability(self.ys_pred[0])
            self.numbers.sort()
            # print('{0} : {1}'.format(n, self.numbers))
            self.list_numbers.append(self.numbers)

        if self.comboBox.currentIndex() <=3:
            for idx,num in enumerate(self.list_numbers):
                self.recommends[idx+4].setPixmap((QtGui.QPixmap("./photo/num"+str(idx+1)+".png")))
                for i in range(6):
                    self.lottoPhotos[self.count].setPixmap(QtGui.QPixmap("./ball_photo/"+str(num[i])+".gif"))
                    self.count+=1
        else:
            for idx,num in enumerate(self.list_numbers):
                self.recommends[idx].setPixmap((QtGui.QPixmap("./photo/num"+str(idx+1)+".png")))
                for i in range(6):
                    self.lottoPhotos[self.count].setPixmap(QtGui.QPixmap("./ball_photo/"+str(num[i])+".gif"))
                    self.count+=1            
        self.progressBar.setProperty("value", 100)

        return self.list_numbers    


app = QApplication([])
a = lottoProcess()
QApplication.processEvents()
sys.exit(app.exec_())



