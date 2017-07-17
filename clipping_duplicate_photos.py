# coding: utf-8
import cv2
import numpy as np
import os
import datetime
import tarfile, io
import time as t
from enum import Enum
import pickle


MEMORY_TAR_1_DORE = []
MEMORY_TAR_2_DORE = []
MEMORY_TAR_3 = []

class Const(Enum):
    TAR_FILES_DIRS = '/path/to/tar/dir/tar_files_dir/'
    VIDEO_FILES_DIR = '/path/to/dit/for /video/files/'


def check_new_tar():
    """
    function to check new tar files in tar dir now NOT USED! Maybe DEPRECATED
    :return: None
    """
    dir_path = '/path/to/tar_files_dir/'
    files = os.listdir(dir_path)
    if len(files) > 0:
        pass


def extract_tar(tar_file_name=None, path=None, extract_path=None):
    """
    Функція яка розпаковує tar архіви
    :param tar_file_name: name of tar file
    :param path: path to tar file
    :param extract_path: path to extract files from tar
    :return: None
    """
    name = tar_file_name.split('.')[0]
    tar_file = tarfile.open(path + tar_file_name, 'r')
    except_txt = list(filter(lambda x: x.endswith('.jpg'), sorted(tar_file.getnames())))
    for file in except_txt:
        f = filter_dor_number_files(file)
        if f == '1':
            if os.path.exists(extract_path + '1' + '/'):
                tar_file.extract(file, path=extract_path + '1' + '/')
            else:
                os.makedirs(extract_path + '1' + '/')
                tar_file.extract(file, path=extract_path + '1' + '/')
        elif f == '2':
            if os.path.exists(extract_path + '2' + '/'):
                tar_file.extract(file, path=extract_path + '2' + '/')
            else:
                os.makedirs(extract_path + '2' + '/')
                tar_file.extract(file, path=extract_path + '2' + '/')
        elif f == '3':
            if os.path.exists(extract_path + '3' + '/'):
                tar_file.extract(file, path=extract_path + '3' + '/')
            else:
                os.makedirs(extract_path + '3' + '/')
                tar_file.extract(file, path=extract_path + '3' + '/')
        else:
            print('HZ 4to ne tak')
    tar_file.close()


def remove_same_files_and_make_video(path=None, video_path=None):
    """
    Головна функція яка формує порізане відео
    :param path: path to dir with JPG files
    :param video_path: path to save video in .avi format
    :return: None
    """
    dirs = os.listdir(path=path)
    for dirsd in dirs:
        count = 0
        except_3 = [i for i in sorted(os.listdir(path=path+dirsd)) if i != '3']
        if len(except_3) > 0:
            for d in except_3:
                files_not_sorted = os.listdir(path=path+dirsd + '/' + d)
                files = sorted(files_not_sorted)
                background = cv2.imread(path + dirsd + '/' + d + '/' + files[0])
                alpha = 0.5
                thresholdLevel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(video_path + '{0}_{1}.avi'.format(dirsd, d), fourcc, 10.0,
                                      (160, 120))

                for file in files:
                    image = cv2.imread(path + dirsd + '/' + d + '/' + file)
                    if files.index(file) > 0:
                        background = (1 - alpha) * image + alpha * background

                    dif = image - background.astype(np.uint8)

                    difGray = cv2.cvtColor(dif, cv2.COLOR_BGR2GRAY)
                    binaryImg = cv2.erode(difGray, thresholdLevel, iterations=1)

                    summa = np.mean(binaryImg)

                    # index = files.index(file)
                    if summa > 30:
                        out.write(image)
                        count += 1
            if count > 30:
                out.release()
            else:
                print('empty video frames')


def filter_dor_number_files(file=None):
    """
    Повертає номер камери(1 - перші двері, 2 - другі двері, 3 - посвідчення)
    :param file: file from tar archive
    :return: 1 or 2 or 3
    """
    f = file.split('_')
    if f[1] == '1':
        return '1'
    elif f[1] == '2':
        return '2'
    else:
        return '3'


def read_pos_txt(dirs_path=None, tar_name=None, tar_path=None):
    """
    Функція читає з тар архіву файл Pos.txt на його основі функція робить висновок про первинний архів та розпаковує
    всі архіви в яких один і той же первинний архів в папку з назвою первинного архіву за допомогою функції(extract_tar)
    :param dirs_path: path to dir with tar archive
    :param tar_name: name of tar archive
    :param tar_path: path to tar archive
    :return: path to dir & number of main tar
    """
    tar_file = tarfile.open(tar_path+tar_name)
    pos_txt = tar_file.extractfile('Pos.txt')
    content = pos_txt.readlines()
    decoded_content = content[-1].decode('utf-8')
    tar_file.close()
    if (decoded_content+'.tar') == tar_name and os.path.exists(dirs_path+decoded_content+'/'):
        extract_tar(path=tar_path, tar_file_name=tar_name, extract_path=dirs_path + decoded_content + '/')
        return dirs_path + decoded_content + '/'
    elif (decoded_content+'.tar') != tar_name and os.path.exists(dirs_path+decoded_content+'/'):
        extract_tar(path=tar_path, tar_file_name=tar_name, extract_path=dirs_path + decoded_content + '/')
        return dirs_path + decoded_content + '/'
    elif (decoded_content+'.tar') != tar_name and not os.path.exists(dirs_path+decoded_content+'/'):
        os.makedirs(dirs_path + decoded_content)
        extract_tar(path=tar_path, tar_file_name=tar_name, extract_path=dirs_path + decoded_content + '/')
        return dirs_path + decoded_content + '/'
    elif (decoded_content+'.tar') == tar_name and not os.path.exists(dirs_path+decoded_content+'/'):
        os.makedirs(dirs_path + decoded_content)
        extract_tar(path=tar_path, tar_file_name=tar_name, extract_path=dirs_path + decoded_content + '/')
        return dirs_path + decoded_content + '/'
    else:
        return '4eto ne tac'


def read_tar_from_memory():
    pass


def read_and_trimming_video(bytes_array=None, video_path=None):
    """
    Видео приймається з буфферу порівнюється та створює кінцеве відео.
    :param bytes_array:
    :param video_path:
    :return:
    """
    alpha = 0.5
    thresholdLevel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    background = cv2.imdecode(np.frombuffer(bytes_array[0], np.uint8), cv2.COLOR_BGR2GRAY)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('./output.avi', fourcc, 10.0, (160, 120))
    count = 0
    for file in bytes_array:

        image = cv2.imdecode(np.frombuffer(file, np.uint8), cv2.COLOR_BGR2GRAY)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if bytes_array.index(file) > 0:
            background = (1 - alpha) * image + alpha * background
        dif = image - background.astype(np.uint8)

        difGray = cv2.cvtColor(dif, cv2.COLOR_BGR2GRAY)
        binaryImg = cv2.erode(difGray, thresholdLevel, iterations=1)

        summa = np.mean(binaryImg)

        index = bytes_array.index(file)
        if summa > 30:
            out.write(image)
            count += 1
    if count > 6:
        out.release()
    else:
        print('pustoi')


def read_tar_to_memory(tar_path=None, tar_name=None, pickle_data=None):
    tar = tarfile.open(tar_path+tar_name)
    filtered_tar = list(filter(lambda x: x.endswith('.jpg'), sorted(tar.getnames())))

    if pickle_data:
        one = pickle_data.get('memory_tar_1_dore')
        two = pickle_data.get('memory_tar_2_dore')
        three = pickle_data.get('memory_tar_3')
        for name in filtered_tar:
            id_dore = filter_dor_number_files(name)
            n = io.BufferedReader(tar.extractfile(name))
            if id_dore == '1':
                one.append(n.peek())
            elif id_dore == '2':
                two.append(n.peek())
            else:
                three.append(n.peek())
        return {'tar_name': tar_name, '1': one, '2': two, '3': three}
    else:
        for name in filtered_tar:
            id_dore = filter_dor_number_files(name)
            n = io.BufferedReader(tar.extractfile(name))
            if id_dore == '1':
                memory_tar_1_dore.append(n.peek())
            elif id_dore == '2':
                memory_tar_2_dore.append(n.peek())
            else:
                memory_tar_3.append(n.peek())
        return {'tar_name': tar_name, '1': memory_tar_1_dore, '2': memory_tar_2_dore, '3': memory_tar_3}
    # read_and_trimming_video(memory_tar)


def create_in_memory_variables_for_cameras(tarname=None, pickle_dict=None):
    tar_file = tarfile.open(name=tarname)
    pos_txt = tar_file.extractfile('Pos.txt')
    content = pos_txt.readlines()
    decoded_content = content[-1].decode('utf-8')
    if (decoded_content+'.tar') == tarname and (decoded_content+'.tar') == pickle_dict['tar_name']:
        read_tar_to_memory()
    elif (decoded_content+'.tar') == tarname and pickle_dict['tar'] != decoded_content:
        pass


def video_trimming(
        dir_path2=Const.TAR_FILES_DIRS.value,
        dir_path3=Const.VIDEO_FILES_DIR.value):
    """
    Головна функція запускає розпаковку архівів та функцію викидання кадрів які повторюються
    :param dir_path2: path to dir with tar archives
    :param dir_path3: path to dir with dirs include photo
    :return: None
    """
    pth = os.listdir(path=dir_path2)
    dirs = os.listdir(path=dir_path3)
    for i in sorted(pth):
        extract_path = read_pos_txt(tar_path=dir_path2, tar_name=i, dirs_path=dir_path3)

    remove_same_files_and_make_video(path=dir_path3, video_path='/home/tito/trimmingvideo/video/')

time1 = t.time()
if __name__ == '__main__':
    # video_trimming()
    _t = read_tar_to_memory(tar_path=Const.TAR_FILES_DIRS.value, tar_name='09839.tar')
time2 = t.time()
print(time2-time1)



