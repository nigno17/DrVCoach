import sys
import random
import os
import torch

from PyQt6.QtCore import QSize, Qt, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QDialog,
    QLineEdit,
    QFrame,
    QComboBox,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
    QSlider
)
from PyQt6.QtMultimedia import QMediaPlayer, QCamera, QMediaCaptureSession, QMediaDevices, QMediaRecorder
from PyQt6.QtMultimediaWidgets import QVideoWidget

from fileManagement import addUser, loadUsers, loadDescription, updateVideoList
from actionDetection import ActionDetector

labels_list = ['forward_arm_rotations', 
               'backward_arm_rotations',
               'lateral_bends', 
               'jumping_jacks',
               'frontal_bends', 
               'hips_rotations',
               'lunges',
               'squats', 
               'seated_torso_rotations',
               'torso_rotations', 
               'bent_torso_rotations']

class NewUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.mainwin = parent
        self.setWindowTitle("Add New User")

        nameLayout = QHBoxLayout()
        title_name = QLabel("Name: ")
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setMaxLength(20)
        self.nameLineEdit.setPlaceholderText("Enter your full name (name, surname)...")
        nameLayout.addWidget(title_name)
        nameLayout.addWidget(self.nameLineEdit)

        ageLayout = QHBoxLayout()
        title_age = QLabel("Age: ")
        self.ageSB = QSpinBox()
        self.ageSB.setRange(18, 150)
        ageLayout.addWidget(title_age)
        ageLayout.addWidget(self.ageSB)

        genderLayout = QHBoxLayout()
        title_gender = QLabel("Gender: ")
        self.genderCB = QComboBox()
        self.genderCB.addItems(["Man", "Woman", "Non-Binary", "Other", "I prefer not to say", ])
        genderLayout.addWidget(title_gender)
        genderLayout.addWidget(self.genderCB)

        button_layout = QHBoxLayout()
        btn = QPushButton("Save User")
        btn.pressed.connect(self.save_user)
        button_layout.addWidget(btn)

        btn = QPushButton("Cancel")
        btn.pressed.connect(self.do_not_save)
        button_layout.addWidget(btn)

        self.layout = QVBoxLayout()
        message = QLabel("New User")
        self.layout.addWidget(message)
        self.layout.addLayout(nameLayout)
        self.layout.addLayout(ageLayout)
        self.layout.addLayout(genderLayout)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def save_user(self):
        user_id = addUser(self.nameLineEdit.text(), self.ageSB.value(), self.genderCB.currentText())
        if self.mainwin:
            self.mainwin.user_info['user_id'] = user_id
            self.mainwin.user_info['user_name'] = self.nameLineEdit.text()
            self.mainwin.user_info['user_age'] = self.ageSB.value()
            self.mainwin.user_info['user_gender'] = self.genderCB.currentText()
        print("Saved")
        self.accept()

    def do_not_save(self):
        print("Not Saved")
        self.reject()

class LoadUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        print(parent)
        self.mainwin = parent
        self.setWindowTitle("Users")

        self.user_list = loadUsers()

        self.listWidget = QListWidget()
        for temp_user in self.user_list:
            self.listWidget.addItem(temp_user['user_name'] + ' - Age: ' + str(temp_user['user_age']))
        self.listWidget.setCurrentRow(0)     

        button_layout = QVBoxLayout()
        btn = QPushButton("Load User")
        btn.pressed.connect(self.load_user)
        button_layout.addWidget(btn)

        btn = QPushButton("Cancel")
        btn.pressed.connect(self.do_not_load)
        button_layout.addWidget(btn)

        self.guiLayout = QHBoxLayout()
        self.guiLayout.addWidget(self.listWidget)
        self.guiLayout.addLayout(button_layout)

        self.layout = QVBoxLayout()
        message = QLabel("User List")
        self.layout.addWidget(message)
        self.layout.addLayout(self.guiLayout)
        self.setLayout(self.layout)

    def load_user(self):
        current_user = self.user_list[self.listWidget.currentRow()]
        if self.mainwin:
            self.mainwin.user_info = current_user
        print("Loaded")
        self.accept()

    def do_not_load(self):
        print("Not Loaded")
        self.reject()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.detector = ActionDetector()
        self.n_eXs = 3
        self.repXexe = 5
        self.curr_exe = 0

        self.exe_path = ''

        self.setGeometry(100, 100, 1024, 768)
        
        self.user_info = {'user_id': 0, 'user_name': '', 'user_age': 0, 'user_gender': ''}

        self.setWindowTitle("Dr. VCoach")

        self.win_layout = self.win_layout_init()

        widget = QWidget()
        widget.setLayout(self.win_layout)
        self.setCentralWidget(widget)

    def win_layout_init(self):
        win_layout = QStackedLayout()
        win_layout.currentChanged.connect(self.currentChangedHandler)
        indexPage_layout = self.indexPage_layout_init()
        introPage_layout = self.introPage_layout_init()
        exercisePage_layout = self.exercisePage_layout_init()
        monitoringPage_layout = self.monitoringPage_layout_init()
        processingPage_layout = self.processingPage_layout_init()
        resultsPage_layout = self.resultsPage_layout_init()
        endPage_layout = self.endPage_layout_init()

        index_widget = QWidget()
        index_widget.setLayout(indexPage_layout)
        win_layout.addWidget(index_widget)
        
        intro_widget = QWidget()
        intro_widget.setLayout(introPage_layout)
        win_layout.addWidget(intro_widget)

        exercise_widget = QWidget()
        exercise_widget.setLayout(exercisePage_layout)
        win_layout.addWidget(exercise_widget)

        monitoring_widget = QWidget()
        monitoring_widget.setLayout(monitoringPage_layout)
        win_layout.addWidget(monitoring_widget)
        
        processing_widget = QWidget()
        processing_widget.setLayout(processingPage_layout)
        win_layout.addWidget(processing_widget)

        results_widget = QWidget()
        results_widget.setLayout(resultsPage_layout)
        win_layout.addWidget(results_widget)

        end_widget = QWidget()
        end_widget.setLayout(endPage_layout)
        win_layout.addWidget(end_widget)

        return win_layout

    def currentChangedHandler(self, index):
        if index == 4:
            self.timerPro.start(500)
            

    def indexPage_layout_init(self):
        indexPage_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        title = QLabel()
        title.setPixmap(QPixmap(".\\images\\nao-logo_text.png").scaledToWidth(self.width()))
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)


        btn = QPushButton("New User")
        btn.pressed.connect(self.newUser_pressed)
        button_layout.addWidget(btn)

        btn = QPushButton("Select Old User")
        btn.pressed.connect(self.loadUser_pressed)
        button_layout.addWidget(btn)

        indexPage_layout.addWidget(title)
        indexPage_layout.addLayout(button_layout)

        return indexPage_layout

    def newUser_pressed(self):
        dlg = NewUserDialog(self)
        if dlg.exec():
            print("Success!")
            print(self.user_info['user_id'])
            print(self.user_info['user_name'])
            print(self.user_info['user_age'])
            print(self.user_info['user_gender'])
            self.introPage_label.setText(self.introPage_label.text() + self.user_info['user_name'])
            self.win_layout.setCurrentIndex(1)
        else:
            print("Cancel!")

    def loadUser_pressed(self):
        dlg = LoadUserDialog(self)
        if dlg.exec():
            print("Success!")
            print(self.user_info['user_id'])
            print(self.user_info['user_name'])
            print(self.user_info['user_age'])
            print(self.user_info['user_gender'])
            self.introPage_label.setText(self.introPage_label.text() + self.user_info['user_name'])
            self.win_layout.setCurrentIndex(1)
        else:
            print("Cancel!")

    def introPage_layout_init(self):
        introPage_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        
        introPage_image = QLabel()
        introPage_image.setPixmap(QPixmap(".\\images\\drvcoach2.png").scaledToWidth(self.width()))
        introPage_image.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.introPage_label = QLabel()
        introPage_text = 'Welcome '
        font = self.introPage_label.font()
        font.setPointSize(30)
        self.introPage_label.setFont(font)
        self.introPage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.introPage_label.setText(introPage_text)

        btn = QPushButton("Start training session")
        btn.pressed.connect(self.start_train_pressed)
        button_layout.addWidget(btn)

        introPage_layout.addWidget(introPage_image)
        introPage_layout.addWidget(self.introPage_label)
        introPage_layout.addLayout(button_layout)

        return introPage_layout

    def start_train_pressed(self):
        self.win_layout.setCurrentIndex(2)

    def exercisePage_layout_init(self):
        exercisePage_layout = QVBoxLayout()
        tools_layout = QHBoxLayout()
        mediaPlayer_widget = self.mediaPlayer_tab()
        button_layout = QHBoxLayout()
        leftMenu_layout = QVBoxLayout()

        exercisePage_label = QLabel()
        exercisePage_text = 'Today exercises'
        font = exercisePage_label.font()
        font.setPointSize(15)
        exercisePage_label.setFont(font)
        exercisePage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        exercisePage_label.setText(exercisePage_text)

        self.exercisePage_description = QLabel()

        listWidgetExe = QListWidget()
        self.current_exe_list = random.sample(labels_list, self.n_eXs)
        for exercise in self.current_exe_list:
            listWidgetExe.addItem(exercise)
        listWidgetExe.currentTextChanged.connect(self.text_changed)
        listWidgetExe.setCurrentRow(0)
        self.media_player.setSource(QUrl.fromLocalFile('Videos/' + listWidgetExe.currentItem().text() + '.mp4'))

        exercisePage_des_label = QLabel()
        exerciseDesLab_text = 'Exercise description'
        font = exercisePage_des_label.font()
        font.setPointSize(15)
        exercisePage_des_label.setFont(font)
        exercisePage_des_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        exercisePage_des_label.setText(exerciseDesLab_text)
        
        leftMenu_layout.addWidget(exercisePage_label)
        leftMenu_layout.addWidget(listWidgetExe)
        leftMenu_layout.addWidget(exercisePage_des_label)
        leftMenu_layout.addWidget(self.exercisePage_description)

        btn = QPushButton("Go back")
        btn.pressed.connect(self.exercise_back_pressed)
        button_layout.addWidget(btn)
        
        btn = QPushButton("Start monitornig")
        btn.pressed.connect(self.exercise_next_pressed)
        button_layout.addWidget(btn)

        tools_layout.addLayout(leftMenu_layout, stretch=1)
        tools_layout.addWidget(mediaPlayer_widget, stretch=1)

        exercisePage_layout.addLayout(tools_layout)
        exercisePage_layout.addLayout(button_layout)

        return exercisePage_layout
    
    def text_changed(self, s):
        self.media_player.setSource(QUrl.fromLocalFile('Videos/' + s + '.mp4'))
        self.exercisePage_description.setText(loadDescription(s))

    def exercise_next_pressed(self):
        self.win_layout.setCurrentIndex(3)
        self.m_camera.start()
    
    def exercise_back_pressed(self):
        self.win_layout.setCurrentIndex(1)

    def mediaPlayer_tab(self):
        self.media_player = QMediaPlayer()
        video_widget = QVideoWidget()
        button_layout = QHBoxLayout()

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_video)

        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(self.pause_video)

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop_video)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)

        self.media_player.setVideoOutput(video_widget)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        button_layout.addWidget(start_button)
        button_layout.addWidget(pause_button)
        button_layout.addWidget(stop_button)

        layout = QVBoxLayout()
        layout.addWidget(video_widget)
        layout.addWidget(self.slider)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        
        return container

    def start_video(self):
        self.media_player.play()

    def pause_video(self):
        self.media_player.pause()

    def stop_video(self):
        self.media_player.stop()

    def set_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def monitoringPage_layout_init(self):
        monitoringPage_layout = QVBoxLayout()
        cameras_layout = QHBoxLayout()

        self.counter_val = 3
        self.rep_val = 1

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_update)

        self.monitoringPage_label = QLabel()
        monitoringPage_text = self.current_exe_list[self.curr_exe].replace('_', ' ')
        font = self.monitoringPage_label.font()
        font.setPointSize(30)
        font.setBold(True)
        self.monitoringPage_label.setFont(font)
        self.monitoringPage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.monitoringPage_label.setText(monitoringPage_text)

        webcam_layout = QVBoxLayout()
        webcam_label = QLabel()
        webcam_text = 'Webcam'
        font = webcam_label.font()
        font.setPointSize(15)
        webcam_label.setFont(font)
        webcam_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        webcam_label.setText(webcam_text)
        camera_widget = self.camera_mon_tab()
        webcam_layout.addWidget(webcam_label, stretch=1)
        webcam_layout.addWidget(camera_widget, stretch=3)

        videoExample_layout = QVBoxLayout()
        videoExample_label = QLabel()
        videoExample_text = 'Trainer example'
        font = videoExample_label.font()
        font.setPointSize(15)
        videoExample_label.setFont(font)
        videoExample_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        videoExample_label.setText(videoExample_text)
        mediaPlayer_widget = self.mediaPlayer_mon_tab()
        videoExample_layout.addWidget(videoExample_label, stretch=1)
        videoExample_layout.addWidget(mediaPlayer_widget, stretch=3)
        
        cameras_layout.addLayout(webcam_layout)
        cameras_layout.addLayout(videoExample_layout)
        
        self.counter_label = QLabel()
        counter_text = "Push \"start training\" when ready"
        font = self.counter_label.font()
        font.setPointSize(30)
        font.setBold(True)
        self.counter_label.setFont(font)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.counter_label.setText(counter_text)

        self.monitoring_button = QPushButton('start training')
        self.monitoring_button.clicked.connect(self.start_training_clicked)

        monitoringPage_layout.addWidget(self.monitoringPage_label, stretch=1)
        monitoringPage_layout.addLayout(cameras_layout, stretch=3)
        monitoringPage_layout.addWidget(self.counter_label, stretch=1)
        monitoringPage_layout.addWidget(self.monitoring_button, stretch=1)

        return monitoringPage_layout

    def start_training_clicked(self):
        self.monitoring_button.setEnabled(False)
        self.monitoring_button.setText('go to results')
        self.monitoring_button.clicked.disconnect()
        self.monitoring_button.clicked.connect(self.go_results_clicked)
        self.counter_label.setText(str(self.counter_val))
        self.timer.start(1000)
        self.m_camera.start()

    def timer_update(self):
        if self.counter_val == 1:
            self.timer.stop()
            
            drVideos_path = os.path.expanduser("~") + "/Videos/DrVCoach_videos/"
            if not os.path.exists(drVideos_path):
                os.makedirs(drVideos_path)
            user_path = drVideos_path + self.user_info['user_name'].replace(' ', '_') + '/'
            if not os.path.exists(user_path):
                os.makedirs(user_path)
            exe_path_name = user_path + self.current_exe_list[self.curr_exe] + '/'
            if not os.path.exists(exe_path_name):
                os.makedirs(exe_path_name)
            n_old_exe = len(next(os.walk(exe_path_name))[1])
            self.exe_path = exe_path_name + str(n_old_exe) + '/'
            if not os.path.exists(self.exe_path):
                os.makedirs(self.exe_path)
            
            self.m_mediaRecorder.setOutputLocation(QUrl.fromLocalFile(self.exe_path + 'REP_' + str(self.rep_val) + '.mp4'))
            self.m_mediaRecorder.record()
            
            self.media_player_mon.setSource(QUrl.fromLocalFile('Videos/' + self.current_exe_list[self.curr_exe] + '.mp4'))
            self.media_player_mon.play()
            self.counter_label.setText('REP ' + str(self.rep_val))

            videoClass = labels_list.index(self.current_exe_list[self.curr_exe])
            updateVideoList(self.exe_path.replace("\\", '/'), 'REP_' + str(self.rep_val), videoClass, 'w')

            self.update_rep()
        self.update_counter()
        if self.counter_val < 3:
            self.counter_label.setText(str(self.counter_val))

    def update_counter(self):
        self.counter_val -= 1
        if self.counter_val < 1:
            self.counter_val = 3

    def update_rep(self):
        self.rep_val += 1
        if self.rep_val > self.repXexe:
            self.rep_val = 1
    
    def go_results_clicked(self):
        self.media_player_res.setSource(QUrl.fromLocalFile(self.exe_path + 'REP_1.mp4'))
        
        self.monitoring_button.setText('start training')
        self.monitoring_button.clicked.disconnect()
        self.monitoring_button.clicked.connect(self.start_training_clicked)

        counter_text = "Push \"start training\" when ready"
        self.counter_label.setText(counter_text)

        self.win_layout.setCurrentIndex(4)

    def mediaPlayer_mon_tab(self):
        self.media_player_mon = QMediaPlayer()
        self.media_player_mon.mediaStatusChanged.connect(self.mediaStatusHandler)
        video_widget_mon = QVideoWidget()

        self.media_player_mon.setVideoOutput(video_widget_mon)
        
        return video_widget_mon
    def mediaStatusHandler(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.rep_val == 1:
                self.m_mediaRecorder.stop()

                self.monitoring_button.setEnabled(True)
                self.m_camera.stop()
                self.counter_label.setText('EXERCISE ' + str(self.curr_exe + 1) + ' FINISHED')
            else:
                self.m_mediaRecorder.stop()

    def camera_mon_tab(self):
        self.m_camera = QCamera(QMediaDevices.defaultVideoInput())
        camera_widget = QVideoWidget()
        
        self.m_mediaRecorder = QMediaRecorder()
        self.m_mediaRecorder.setVideoFrameRate(30)
        self.m_mediaRecorder.recorderStateChanged.connect(self.recorderStateHandler)

        self.mediaCaptureSession = QMediaCaptureSession()
        self.mediaCaptureSession.setCamera(self.m_camera)
        self.mediaCaptureSession.setVideoOutput(camera_widget)
        self.mediaCaptureSession.setRecorder(self.m_mediaRecorder)

        return camera_widget

    def recorderStateHandler(self, state):
        if state == QMediaRecorder.RecorderState.StoppedState:
            if self.rep_val > 1:
                self.m_mediaRecorder.setOutputLocation(QUrl.fromLocalFile(self.exe_path + 'REP_' + str(self.rep_val) + '.mp4'))
                self.m_mediaRecorder.record()

                self.media_player_mon.play()
                self.counter_label.setText('REP ' + str(self.rep_val))

                videoClass = labels_list.index(self.current_exe_list[self.curr_exe])
                updateVideoList(self.exe_path.replace("\\", '/'), 'REP_' + str(self.rep_val), videoClass)
                
                self.update_rep()

    def processingPage_layout_init(self):
        processingPage_layout = QVBoxLayout()

        self.timerPro = QTimer()
        self.timerPro.timeout.connect(self.timerPro_update)

        processingPage_label = QLabel()
        processingPage_text = 'Processing videos\nPlease wait...'
        font = processingPage_label.font()
        font.setPointSize(30)
        font.setBold(True)
        processingPage_label.setFont(font)
        processingPage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        processingPage_label.setText(processingPage_text)

        processingPage_layout.addWidget(processingPage_label)

        return processingPage_layout

    def timerPro_update(self):
        self.timerPro.stop()
        self.results = []
        for i in range(self.repXexe):
            self.results.append(self.detector.testVideo(self.exe_path.replace("\\", '/') + 'REP_'+ str(i + 1) + '.mp4'))

            item = self.listWidgetRes.item(i)
            correctLabel = labels_list.index(self.current_exe_list[self.curr_exe])
            if self.results[i][0][0] == correctLabel:
                item.setIcon(QIcon('images/green_icon.png'))
            elif self.results[i][1][0] == correctLabel or self.results[i][2][0] == correctLabel:
                item.setIcon(QIcon('images/yellow_icon.png'))
            else:
                item.setIcon(QIcon('images/red_icon.png'))
        print(self.results)
        torch.save(self.results, self.exe_path + 'results.pt')
           
        self.listWidgetRes.setCurrentRow(0)
        self.win_layout.setCurrentIndex(5)
    
    def resultsPage_layout_init(self):
        resultsPage_layout = QVBoxLayout()
        tools_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        mediaPlayer_widget = self.mediaPlayer_res_tab()
        leftMenu_layout = QVBoxLayout()

        self.resultsPage_label = QLabel()
        resultsPage_text = "\"" + self.current_exe_list[self.curr_exe].replace('_', ' ') + "\" repetitions list"
        font = self.resultsPage_label.font()
        font.setPointSize(15)
        self.resultsPage_label.setFont(font)
        self.resultsPage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.resultsPage_label.setText(resultsPage_text)

        self.resultsPage_description = QLabel()

        self.listWidgetRes = QListWidget()
        for repetition in range(self.repXexe):
            self.listWidgetRes.addItem('REP_' + str(repetition + 1))
        self.listWidgetRes.currentTextChanged.connect(self.text_changed_res)

        resultsPage_des_label = QLabel()
        resultsDesLab_text = 'Predictions'
        font = resultsPage_des_label.font()
        font.setPointSize(15)
        resultsPage_des_label.setFont(font)
        resultsPage_des_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        resultsPage_des_label.setText(resultsDesLab_text)
        
        leftMenu_layout.addWidget(self.resultsPage_label)
        leftMenu_layout.addWidget(self.listWidgetRes)
        leftMenu_layout.addWidget(resultsPage_des_label)
        leftMenu_layout.addWidget(self.resultsPage_description)
        
        btn = QPushButton("Next exercise")
        btn.pressed.connect(self.results_next_pressed)
        button_layout.addWidget(btn)

        tools_layout.addLayout(leftMenu_layout)
        tools_layout.addWidget(mediaPlayer_widget)

        resultsPage_layout.addLayout(tools_layout)
        resultsPage_layout.addLayout(button_layout)

        return resultsPage_layout
    
    def text_changed_res(self, s):
        self.media_player_res.setSource(QUrl.fromLocalFile(self.exe_path + s + '.mp4'))
        
        act_index = int(s.replace('REP_', '')) - 1

        predText = ''
        for (action, acc) in self.results[act_index]:
            predText += f"{labels_list[action]:<50}{(acc * 100):.2f}%\n"
    
        self.resultsPage_description.setText(predText)

    def results_next_pressed(self):
        self.curr_exe += 1

        if self.curr_exe < self.n_eXs:
            monitoringPage_text = self.current_exe_list[self.curr_exe].replace('_', ' ')
            self.monitoringPage_label.setText(monitoringPage_text)

            resultsPage_text = "\"" + self.current_exe_list[self.curr_exe].replace('_', ' ') + "\" repetitions list"
            self.resultsPage_label.setText(resultsPage_text)
            
            self.win_layout.setCurrentIndex(3)
            self.m_camera.start()
        else:
            self.win_layout.setCurrentIndex(6)

    def mediaPlayer_res_tab(self):
        self.media_player_res = QMediaPlayer()
        video_widget = QVideoWidget()
        button_layout = QHBoxLayout()

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_video_res)

        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(self.pause_video_res)

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop_video_res)

        self.slider_res = QSlider(Qt.Orientation.Horizontal)
        self.slider_res.sliderMoved.connect(self.set_position_res)

        self.media_player_res.setVideoOutput(video_widget)
        self.media_player_res.positionChanged.connect(self.position_changed_res)
        self.media_player_res.durationChanged.connect(self.duration_changed_res)

        button_layout.addWidget(start_button)
        button_layout.addWidget(pause_button)
        button_layout.addWidget(stop_button)

        layout = QVBoxLayout()
        layout.addWidget(video_widget)
        layout.addWidget(self.slider_res)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        
        return container

    def start_video_res(self):
        self.media_player_res.play()

    def pause_video_res(self):
        self.media_player_res.pause()

    def stop_video_res(self):
        self.media_player_res.stop()

    def set_position_res(self, position):
        self.media_player_res.setPosition(position)

    def position_changed_res(self, position):
        self.slider_res.setValue(position)

    def duration_changed_res(self, duration):
        self.slider_res.setRange(0, duration)

    def endPage_layout_init(self):
        endPage_layout = QVBoxLayout()

        endPage_label = QLabel()
        endPage_text = 'Session ended\nGreat Job!'
        font = endPage_label.font()
        font.setPointSize(30)
        font.setBold(True)
        endPage_label.setFont(font)
        endPage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        endPage_label.setText(endPage_text)

        endPage_layout.addWidget(endPage_label)

        return endPage_layout


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
