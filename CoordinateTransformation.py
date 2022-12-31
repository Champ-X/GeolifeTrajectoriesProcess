import os
import math
import time
from tqdm import tqdm

a = 6378137
b = 6356752
# e = math.sqrt(a ** 2 - b ** 2) / a
# 离心率e = 0.08181979099211441
e = 0.08181979099211441


def CoordinateTransformation(new_dir, file_name, inputpath, timeslot=5):
    data_dict = {}
    current_period = 0
    period_start_flag = True
    with open(inputpath, 'r', encoding='utf-8') as infile:
        for line in infile:
            data_line = line.strip("\n").split(',')
            if len(data_line) != 7:
                continue
            # 坐标转换
            B = eval(data_line[0])
            L = eval(data_line[1])
            H = eval(data_line[3])
            N = a / math.sqrt(1 - (e**2) * (math.sin(B)**2))
            x = "%e" % ((N + H)*math.cos(B)*math.cos(L))
            y = "%e" % ((N + H) * math.cos(B) * math.sin(L))
            z = "%e" % ((N*(1 - e**2) + H) * math.sin(B))

            # 根据时间戳判断处于哪个时间段
            current_timestamp = time.mktime(time.strptime(data_line[5] + ' ' + data_line[6], "%Y-%m-%d %H:%M:%S"))
            if period_start_flag:
                current_period += 1
                data_dict[current_period] = []
                data_dict[current_period].append((x, y))
                pre_timestamp = current_timestamp
                period_start_flag = False
            else:
                if (current_timestamp - pre_timestamp) != timeslot:
                    current_period += 1
                    data_dict[current_period] = []
                    data_dict[current_period].append((x, y))
                    pre_timestamp = current_timestamp
                else:
                    pre_timestamp = current_timestamp
                    data_dict[current_period].append((x, y))

    for period in data_dict.keys():
        data_list = data_dict[period]
        filepath = './' + new_dir + '/' + file_name + '_' + str(period) + '.txt'
        with open(filepath, 'w', encoding='utf-8') as fileByPeriod:
            for coordinate_tuple in data_list:
                coordinate = str(coordinate_tuple[0]) + ' ' + str(coordinate_tuple[1]) + '\n'
                fileByPeriod.write(coordinate)


if __name__ == "__main__":
    data_dir = "data"
    os.mkdir("processed_data")
    # # 删除labels.txt文件
    # dir_list = os.listdir(data_dir)
    # for dir in dir_list:
    #     file_list = os.listdir(data_dir + '/' + dir)
    #     if file_list.__contains__('labels.txt'):
    #         os.remove(data_dir + '/' + dir + '/labels.txt')
    
    dir_list = os.listdir(data_dir)
    for dir in dir_list:
        txt_list = os.listdir(data_dir + '/' + dir + '/' + 'Trajectory')
        new_dir = "processed_data/" + dir + "_processed"
        os.mkdir(new_dir)
        for txt_path in tqdm(txt_list, colour="blue", desc=f'{dir} processing......'):
            file_name = txt_path[:-4]  # txt或plt文件名称(去除.txt)
            CoordinateTransformation(new_dir, file_name, data_dir
                                     + '/' + dir + '/' + 'Trajectory' + '/' + txt_path)

