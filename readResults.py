import sys
import os
import torch
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np

from fileManagement import addUser, loadUsers, loadDescription, updateVideoList

# fullResults = [{'user_info': <user>, 'exercises': <exercises>}]
# 
# user = {'user_name': <string>, 'user_age': <int>, 'user_gender': <string>, 'user_id': <int>}
# exercises = [{'name': <string>, 'sessions': <sessions>}]
# 
# sessions = [{'session_number': <int>, 'results': <results>}]
# 
# results = [<repetitions>]
# repetitions = [(exercise_class, accuracy)]
# exercise_class = <int>
# accuracy = <float>

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

abb_labels_list = ['fw_arm_rot', 
                   'bw_arm_rot',
                   'lat_bends', 
                   'jump_jacks',
                   'front_bends', 
                   'hips_rot',
                   'lunges',
                   'squats', 
                   'seated_torso_rot',
                   'torso_rot', 
                   'bent_torso_rot']

sus_questions_list = ['I think that I would like to use this system frequently', 
                      'I found the system unnecessarily complex',
                      'I thought the system was easy to use', 
                      'I think that I would need the support of a technical person to be able to use this system',
                      'I found the various functions in this system were well integrated', 
                      'I thought there was too much inconsistency in this system',
                      'I would imagine that most people would learn to use this system very quickly',
                      'I found the system very cumbersome to use', 
                      'I felt very confident using the system',
                      'I needed to learn a lot of things before I could get going with this system']

train_questions_list = ['How would you assess the quality of a training session using DrVCoach?', 
                        'How would you rate the clarity of instructions on performing exercises using DrVCoach software?',
                        'How would you rate quality of DrVCoach software\'s evaluation of the performed exercise?']

sus_scores = [[1, 2, 3, 3, 4, 5, 5, 5, 5],
              [1, 1, 1, 1, 1, 2, 2, 2, 3],
              [3, 4, 4, 5, 5, 5, 5, 5, 5],
              [1, 1, 1, 1, 1, 2, 2, 4, 5],
              [4, 5, 5, 5, 5, 5, 5, 5, 5],
              [1, 1, 1, 1, 1, 1, 1, 1, 4],
              [3, 5, 5, 5, 5, 5, 5, 5, 5],
              [1, 1, 1, 1, 1, 1, 1, 3, 5],
              [4, 4, 5, 5, 5, 5, 5, 5, 5],
              [1, 1, 1, 1, 1, 1, 3, 3, 4]]

train_scores = [[4, 4, 4, 4, 5, 5, 5, 5, 5],
                [4, 5, 5, 5, 5, 5, 5, 5, 5],
                [3, 4, 4, 4, 5, 5, 5, 5, 5]]

def plotAcc(x_labels, top1_, top3_, title):
    accuracy_val = {
        'Top-1': top1_,
        'Top-3': top3_,
    }

    x = np.arange(len(x_labels))  # the label locations
    width = 0.35  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in accuracy_val.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Accuracy (percentage)')
    ax.set_title(title)
    ax.set_xticks(x + width/2, x_labels)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 110)

    plt.show()

def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i]//2, y[i], ha = 'center')

def plotSesNum(x_labels, counts, title):
    fig, ax = plt.subplots()

    ax.bar(x_labels, counts, color='tab:orange')
    addlabels(x_labels, counts)

    ax.set_ylabel('number of sessions')
    ax.set_title(title)

    plt.show()

def plotSUS(y_labels, mean, std, title, x_label):
    fig, ax = plt.subplots()

    y_pos = np.arange(len(y_labels))

    # ax.barh(y_pos, mean, xerr=std, align='center', color='tab:orange')
    ax.barh(y_pos, mean, align='center', color='tab:orange')
    ax.set_yticks(y_pos, labels=y_labels)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel(x_label)
    ax.set_xticks(np.arange(1, 6, 1))
    ax.set_xlim(1, 5)
    ax.set_title(title)

    plt.subplots_adjust(left=0.5)

    plt.show()

if __name__ == "__main__":
    videosPath = os.path.expanduser("~") + "/Videos/DrVCoach_videos/"
    usersPath = os.path.expanduser("~") + "/Documents/Projects/DrVCoach/Users/"

    userList = loadUsers(usersPath)

    itr = iter(os.walk(videosPath))
    (dirpath, dirnames, filenames) = next(itr)
    subjects = dirnames

    abbSubList = []
    for sub in range(len(subjects)):
        abbSubList.append('Sub' + str(sub + 1))

    fullResults = []
    for idx, uName in enumerate(subjects):
        userPath = videosPath + uName + '/'
        itr = iter(os.walk(userPath))
        (dirpath, dirnames, filenames) = next(itr)
        exercises = dirnames

        userExe = []
        for exe in exercises:
            exePath = userPath + exe + '/'
            itr = iter(os.walk(exePath))
            (dirpath, dirnames, filenames) = next(itr)
            sessions = dirnames

            sesList = []
            for ses in sessions:
                sesPath = exePath + ses + '/'
                res = torch.load(sesPath + 'results.pt')

                new_ses = {}
                new_ses['session_number'] = int(ses)
                new_ses['results'] = res
                sesList.append(new_ses)

            new_exe = {}
            new_exe['name'] = exe.replace('_', ' ')
            new_exe['sessions'] = sesList
            userExe.append(new_exe)

        for user in userList:
            if user['user_name'] == uName.replace('_', ' '):
                new_user = {}
                new_user['user_info'] = user
                new_user['user_info']['user_id'] = idx
                new_user['exercises'] = userExe
                fullResults.append(new_user)
    
    for results in fullResults:
        print(results['user_info'])
    print('------------------------------')

    sessionsXexe = [0] * len(labels_list)
    for results in fullResults:
        for exe in results['exercises']:
            exClassIdx = labels_list.index(exe['name'].replace(' ', '_'))
            exNumSess = len(exe['sessions'])

            sessionsXexe[exClassIdx] += exNumSess

    plotSesNum(abb_labels_list, sessionsXexe, 'Number of sessions by exercise')

    print(sessionsXexe)
    print('------------------------------')

    top1 = [0] * len(labels_list)
    top3 = [0] * len(labels_list)
    totalEx = [0] * len(labels_list)
    for results in fullResults:
        for exe in results['exercises']:
            exClassIdx = labels_list.index(exe['name'].replace(' ', '_'))
            for ses in exe['sessions']:
                for rep in ses['results']:
                    totalEx[exClassIdx] += 1
                    if rep[0][0] == exClassIdx:
                        top1[exClassIdx] += 1
                        top3[exClassIdx] += 1
                    if rep[1][0] == exClassIdx or rep[2][0] == exClassIdx:
                        top3[exClassIdx] += 1
    for exe in range(len(labels_list)):
        top1[exe] = round(top1[exe] / totalEx[exe] * 100, 2)
        top3[exe] = round(top3[exe] / totalEx[exe] * 100, 2)

    plotAcc(abb_labels_list, top1, top3, 'Top-1 and Top-3 accuracy by exercise')

    print(top1)
    print(top3)
    print('------------------------------')
    
    top1sub = [0] * len(subjects)
    top3sub = [0] * len(subjects)
    totalSub = [0] * len(subjects)
    for results in fullResults:
        userId = results['user_info']['user_id']
        for exe in results['exercises']:
            exClassIdx = labels_list.index(exe['name'].replace(' ', '_'))
            for ses in exe['sessions']:
                for rep in ses['results']:
                    totalSub[userId] += 1
                    if rep[0][0] == exClassIdx:
                        top1sub[userId] += 1
                        top3sub[userId] += 1
                    if rep[1][0] == exClassIdx or rep[2][0] == exClassIdx:
                        top3sub[userId] += 1
    for sub in range(len(subjects)):
        top1sub[sub] = round(top1sub[sub] / totalSub[sub] * 100, 2)
        top3sub[sub] = round(top3sub[sub] / totalSub[sub] * 100, 2)

    plotAcc(abbSubList, top1sub, top3sub, 'Top-1 and Top-3 accuracy by subject')

    print(top1sub)
    print(top3sub)
    print('------------------------------')

    sus_mean = np.mean(sus_scores, 1)
    sus_std = np.std(sus_scores, 1)

    title = 'Results on SUS questions'
    x_label = 'Agreement level (strongly disagree -> strongly agree)'

    plotSUS(sus_questions_list, sus_mean, sus_std, title, x_label)
    print('------------------------------')

    train_mean = np.mean(train_scores, 1)
    train_std = np.std(train_scores, 1)

    title = 'Results on questions about the training session'
    x_label = 'Rating (low -> high)'

    plotSUS(train_questions_list, train_mean, train_std, title, x_label)
    print('------------------------------')