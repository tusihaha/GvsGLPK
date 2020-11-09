import os
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import pchip, BSpline
from Graph.timetable import timetable
from GLPK.genmod import genmod

def gencase(teachers, courses, rooms):
    e1 = list()
    e2 = list()

    e_check = list()

    for i in range(teachers - 1):
        c = random.randint(1, courses)
        index = random.randint(1, courses - c + 1)
        for j in range(1, c + 1):
            if index not in e_check:
                e_check.append(index)
            e1.append(('T' + str(i + 1), 'C' + str(index)))
            index = random.randint(index + 1, courses - (c - j) + 1)
    for i in range(1, courses + 1):
        if i not in e_check:
            e1.append(('T' + str(teachers), 'C' + str(i)))

    e_check = list()

    for i in range(rooms - 1):
        c = random.randint(1, courses)
        index = random.randint(1, courses - c + 1)
        for j in range(1, c + 1):
            if index not in e_check:
                e_check.append(index)
            e2.append(('R' + str(i + 1), 'C' + str(index)))
            index = random.randint(index + 1, courses - (c - j) + 1)
    for i in range(1, courses + 1):
        if i not in e_check:
            e2.append(('R' + str(rooms), 'C' + str(i)))

    ce1 = dict()
    for (t, c) in e1:
        st = int(t[1:]) - 1
        if st not in ce1:
            ce1[st] = [int(c[1:]) - 1]
        else:
            ce1[st].append(int(c[1:]) - 1)
    for i in range(teachers):
        if i not in ce1:
            ce1[i] = list()
    exce1 = dict()
    for i in ce1:
        exce1[i] = list()
        for j in range(courses):
            if j not in ce1[i]:
                exce1[i].append(j)

    ce2 = dict()
    for (r, c) in e2:
        sr = int(r[1:]) - 1
        if sr not in ce2:
            ce2[sr] = [int(c[1:]) - 1]
        else:
            ce2[sr].append(int(c[1:]) - 1)
    for i in range(rooms):
        if i not in ce2:
            ce2[i] = list()
    exce2 = dict()
    for i in ce2:
        exce2[i] = list()
        for j in range(courses):
            if j not in ce2[i]:
                exce2[i].append(j)

    return [e1, e2, exce1, exce2]

def count_timeslot(filename):
    f = open(filename, 'r')
    lines = f.readlines()

    largest_timeslot = 0
    for line in lines:
        c = line.split(' ')
        if len(c) == 5 and c[0] == 'result:':
            current_timeslot = int(c[4][5:].strip())
            if current_timeslot > largest_timeslot:
                largest_timeslot = current_timeslot
    
    f.close()

    f = open(filename, 'a')
    f.write('\nTimeslot used: ' + str(largest_timeslot + 1) + '\n')
    f.close()

def get_info(number, count, first_char):
    time_used_glpk = []
    timeslot_used_glpk = []
    for i in range(1, count + 1):
        f = open(first_char + str(number + 1) + 'glpk_result' + str(int(i)) + '.txt', 'r')
        lines = f.readlines()
        for line in lines:
            c = line.split(' ')
            while '' in c:
                c.remove('')
            if len(c) == 4 and c[0] == 'Time':
                time_used_glpk.append(float(c[2]))
            elif len(c) == 3 and c[0] == 'Timeslot':
                timeslot_used_glpk.append(int(c[2]))
    time_used_graph = []
    timeslot_used_graph = []
    for i in range(1, count + 1):
        f = open(first_char + str(number + 1) + 'graph_result' + str(int(i)) + '.txt', 'r')
        lines = f.readlines()
        for line in lines:
            c = line.split(' ')
            while '' in c:
                c.remove('')
            if len(c) == 3 and c[0] == 'Executed':
                time_used_graph.append(float(c[2]))
            elif len(c) == 3 and c[0] == 'Timeslot':
                timeslot_used_graph.append(int(c[2]))
    return [time_used_glpk, timeslot_used_glpk, time_used_graph, timeslot_used_graph]


if __name__ == "__main__":
    # Courses series:
    series = [(10, 10), (5, 15), (20, 25), (30, 30)]
    step = 4
    count = range(step, 101, step)
    first_char = 'c'
    
    
    for s in range(len(series)):
        for i in count:
            order = [series[s][0], i, series[s][1]]

            [e1, e2, exce1, exce2] = gencase(order[0], order[1], order[2])
            timeslots = timetable(e1, e2, first_char + str(s + 1) + 'graph_result' + str(int(i/step)) + '.txt')
            genmod(order[0], order[1], order[2], timeslots, exce1, exce2, first_char  + str(s + 1) + 'gen' + str(int(i/step)) + '.mod')
            os.system('glpsol --model ' + first_char + str(s + 1) + 'gen' + str(int(i/step)) + '.mod > ' + first_char + str(s + 1) + 'glpk_result' + str(int(i/step)) + '.txt')
            count_timeslot(first_char + str(s + 1) + 'glpk_result' + str(int(i/step)) + '.txt')
    

    arr_count = np.array(count)

    for i in range(len(series)):
        [time_used_glpk, timeslot_used_glpk, time_used_graph, timeslot_used_graph] = get_info(i, len(count), first_char)
        fig, axs = plt.subplots(2,1)
        axs[0].set_title(str(series[i][0]) + ' teachers, ' + str(series[i][1]) + ' rooms')
        axs[0].set_xlabel('Courses')
        axs[0].set_ylabel('Time (second)')

        time_used_glpk = np.array(time_used_glpk)
        time_used_graph = np.array(time_used_graph)

        smooth_count = np.linspace(arr_count.min(), arr_count.max(), 240)
        pch = pchip(arr_count, time_used_glpk)
        smooth_time_used_glpk = pch(smooth_count)
        pch = pchip(arr_count, time_used_graph)
        smooth_time_used_graph = pch(smooth_count)
        axs[0].plot(smooth_count, smooth_time_used_glpk, marker='.', markevery = 10)
        axs[0].plot(smooth_count, smooth_time_used_graph, marker='.', markevery = 10)

        axs[1].axis('tight')
        axs[1].axis('off')
        columns = tuple(count)
        rows = ['GLPK', 'Graph']
        axs[1].table(cellText = [timeslot_used_glpk, timeslot_used_graph], rowLabels = rows, colLabels = columns, loc='center')
        fig.savefig(first_char + str(i + 1) + '.png')


    # Teachers series:
    series = [(20, 10), (30, 15), (20, 25), (50, 30)]
    step = 4
    count = range(step, 101, step)
    first_char = 't'
    
    
    for s in range(len(series)):
        for i in count:
            order = [i, series[s][0], series[s][1]]

            [e1, e2, exce1, exce2] = gencase(order[0], order[1], order[2])
            timeslots = timetable(e1, e2, first_char + str(s + 1) + 'graph_result' + str(int(i/step)) + '.txt')
            genmod(order[0], order[1], order[2], timeslots, exce1, exce2, first_char  + str(s + 1) + 'gen' + str(int(i/step)) + '.mod')
            os.system('glpsol --model ' + first_char + str(s + 1) + 'gen' + str(int(i/step)) + '.mod > ' + first_char + str(s + 1) + 'glpk_result' + str(int(i/step)) + '.txt')
            count_timeslot(first_char + str(s + 1) + 'glpk_result' + str(int(i/step)) + '.txt')
    

    for i in range(len(series)):
        [time_used_glpk, timeslot_used_glpk, time_used_graph, timeslot_used_graph] = get_info(i, len(count), first_char)
        fig, axs = plt.subplots(2,1)
        axs[0].set_title(str(series[i][0]) + ' courses, ' + str(series[i][1]) + ' rooms')
        axs[0].set_xlabel('Teachers')
        axs[0].set_ylabel('Time (second)')

        time_used_glpk = np.array(time_used_glpk)
        time_used_graph = np.array(time_used_graph)

        smooth_count = np.linspace(arr_count.min(), arr_count.max(), 240)
        pch = pchip(arr_count, time_used_glpk)
        smooth_time_used_glpk = pch(smooth_count)
        pch = pchip(arr_count, time_used_graph)
        smooth_time_used_graph = pch(smooth_count)
        axs[0].plot(smooth_count, smooth_time_used_glpk, marker='.', markevery = 10)
        axs[0].plot(smooth_count, smooth_time_used_graph, marker='.', markevery = 10)
        
        axs[1].axis('tight')
        axs[1].axis('off')
        columns = tuple(count)
        rows = ['GLPK', 'Graph']
        axs[1].table(cellText = [timeslot_used_glpk, timeslot_used_graph], rowLabels = rows, colLabels = columns, loc='center')
        fig.savefig(first_char + str(i + 1) + '.png')


    # Rooms series:
    series = [(10, 20), (15, 30), (25, 20), (30, 50)]
    step = 4
    count = range(step, 101, step)
    first_char = 'r'
    
    
    for s in range(len(series)):
        for i in count:
            order = [series[s][0], series[s][1], i]

            [e1, e2, exce1, exce2] = gencase(order[0], order[1], order[2])
            timeslots = timetable(e1, e2, first_char + str(s + 1) + 'graph_result' + str(int(i/step)) + '.txt')
            genmod(order[0], order[1], order[2], timeslots, exce1, exce2, first_char  + str(s + 1) + 'gen' + str(int(i/step)) + '.mod')
            os.system('glpsol --model ' + first_char + str(s + 1) + 'gen' + str(int(i/step)) + '.mod > ' + first_char + str(s + 1) + 'glpk_result' + str(int(i/step)) + '.txt')
            count_timeslot(first_char + str(s + 1) + 'glpk_result' + str(int(i/step)) + '.txt')
    

    for i in range(len(series)):
        [time_used_glpk, timeslot_used_glpk, time_used_graph, timeslot_used_graph] = get_info(i, len(count), first_char)
        fig, axs = plt.subplots(2,1)
        axs[0].set_title(str(series[i][0]) + ' teachers, ' + str(series[i][1]) + ' courses')
        axs[0].set_xlabel('Rooms')
        axs[0].set_ylabel('Time (second)')
        
        time_used_glpk = np.array(time_used_glpk)
        time_used_graph = np.array(time_used_graph)

        smooth_count = np.linspace(arr_count.min(), arr_count.max(), 240)
        pch = pchip(arr_count, time_used_glpk)
        smooth_time_used_glpk = pch(smooth_count)
        pch = pchip(arr_count, time_used_graph)
        smooth_time_used_graph = pch(smooth_count)
        axs[0].plot(smooth_count, smooth_time_used_glpk, marker='.', markevery = 10)
        axs[0].plot(smooth_count, smooth_time_used_graph, marker='.', markevery = 10)

        axs[1].axis('tight')
        axs[1].axis('off')
        columns = tuple(count)
        rows = ['GLPK', 'Graph']
        axs[1].table(cellText = [timeslot_used_glpk, timeslot_used_graph], rowLabels = rows, colLabels = columns, loc='center')
        fig.savefig(first_char + str(i + 1) + '.png')



