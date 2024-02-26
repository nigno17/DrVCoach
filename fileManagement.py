import sys
import os


def addUser(u_name, u_age, u_gender, usersPath = "Users/"):
    user_id = 0
    for (dirpath, dirnames, filenames) in os.walk(usersPath):
        for filename in filenames:
            if filename != None and ".txt" in filename:
                current_id = eval(filename.replace(".txt", ""))
                if user_id < current_id:
                    user_id = current_id
    user_id = user_id + 1

    file_name = str(user_id) + '.txt'

    u_file = open(usersPath + file_name, 'w')

    u_file.write('Name: ' + u_name + "\n")
    u_file.write('Age: ' + str(u_age) + "\n")
    u_file.write('Gender: ' + u_gender)

    u_file.close()

    return user_id

def loadUsers(usersPath = "Users/"):
    user_list = []
    for (dirpath, dirnames, filenames) in os.walk(usersPath):
        for filename in filenames:
            if filename != None and ".txt" in filename:
                u_file = open(usersPath + filename, 'r')
                Lines = u_file.readlines()
                new_user = {}
                for line in Lines:
                    if 'Name: ' in line:
                        new_user['user_name'] = line.replace('Name: ', '').replace("\n", '')
                    elif 'Age: ' in line:
                        new_user['user_age'] = eval(line.replace('Age: ', ''))
                    elif 'Gender: ' in line:
                        new_user['user_gender'] = line.replace('Gender: ', '')
                new_user['user_id'] = eval(filename.replace(".txt", ""))
                user_list.append(new_user)
                u_file.close()              

    return user_list

def loadDescription(exeName):
    if os.path.isfile('Descriptions/' + exeName + '.txt'):
        u_file = open('Descriptions/' + exeName + '.txt', 'r')

        Lines = u_file.readlines()
        exeDes = ''
        for line in Lines:
            exeDes += line
        u_file.close()
    else:
        exeDes = 'No description found for this exercise'          

    return exeDes

def updateVideoList(videoPath, videoName, videoClass, writeMode = 'a'):
    v_file = open(videoPath + 'video_list.txt', writeMode)

    v_file.write(videoPath + videoName + '.mp4 ' + str(videoClass) + "\n")

    v_file.close()