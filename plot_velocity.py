import matplotlib.pyplot as plt
import numpy as np
import json

# plot velocity field
def vplot(fname, X1, Y1, X2, Y2):
    U, V = X2-X1, Y2-Y1

    fig, ax1 = plt.subplots()
    plt.gca().invert_yaxis()
    q = ax1.quiver(X1, Y1, U, V, color = 'r', angles = 'xy', scale_units='xy', scale= 0.1)
    p1 = ax1.scatter(X1, Y1, 3)


    # ax.quiverkey(q, X=0.3, Y=1.1, U=10,
    #              label='Quiver key, length = 10', labelpos='E')

    plt.savefig(fname)


# interpret dictionary
def get_midpoints(dict):
    mid_x_list = []
    mid_y_list = []
    for i in dict:
        mid_x_interval = []
        mid_y_interval = []
        for j in dict[i]:
            mid_x_frame = []
            mid_y_frame = []
            for k in dict[i][j]:
                mid_x = dict[i][j][k]['mid x']
                mid_y = dict[i][j][k]['mid y']
                mid_x_frame.append(mid_x)
                mid_y_frame.append(mid_y)
            mid_x_interval.append(np.array(mid_x_frame))
            mid_y_interval.append(np.array(mid_y_frame))
        mid_x_list.append(np.array(mid_x_interval))
        mid_y_list.append(np.array(mid_y_interval))
    # mid_x_list = np.array(mid_x_list)
    # mid_y_list = np.array(mid_y_list)
    return mid_x_list, mid_y_list


# # f = 'xyt/xyt_interval.txt'
# f = 'Pos0/Pos0_interval.txt'
# dict = open(f, 'r').read()
# dict = eval(dict)
#
# mid_x, mid_y = get_midpoints(dict)
#
#
#
# for i in range(len(mid_x)):
#     fname = 'Pos0/Pos0' + str(i) + '.png'
#     X1 = mid_x[i][0]
#     X2 = mid_x[i][1]
#     Y1 = mid_y[i][0]
#     Y2 = mid_y[i][1]
#     vplot(fname, X1, Y1, X2, Y2)
