import sys
import os
import chardet
import shutil

'''
the encoding of text in windows is GB2312, but in linux is utf8
I need to change txt encoding
'''
print(__doc__)

def ch_encode(path):
    files = os.listdir(path)
    print(files)
    id_list = []
    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            continue

        ch_file = 'ch_' + file
        fs = open(os.path.join(path, 'news', ch_file), 'w', encoding='utf8')
        with open(os.path.join(path, file), 'r', encoding='GBK') as f:
            for line in f.readlines():
                nid = line.strip().split('\t')[0]
                if nid in id_list:   # unique the news
                    continue
                fs.write(line)

        fs.close()
        print('finish change encode and unique news')

    # f = open('./data/news/ch_net_news_1.txt','rb')
    # lines = f.read()
    # print(chardet.detect(lines))   # show the file encoding
    # f.close()


def rename_file(path):
    files = os.listdir(path)
    print(files)
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            # shutil.move(file_path,os.path.join(path,file.strip('ch_')))
            # re_name = file.strip('ch_')
            re_name = 'ch_' + file
            newName_path = os.path.join(path,re_name)
            os.rename(file_path, newName_path)
        print('finish rename')


def unique_content(path):
    files = os.listdir(path)
    print(files)

    for file in files:
        id_list = []
        if file.__contains__('label'):
            # print(file,'contains label')
            continue
        if os.path.isfile(os.path.join(path, file)) :
            fs = open(os.path.join(path, '../', file), 'w', encoding='utf8')
            with open(os.path.join(path, file), 'r', encoding='utf8') as f:
                for line in f.readlines():
                    nid = line.strip().split('\t')[0]
                    print(nid)
                    if nid in id_list:
                        continue
                    else :
                        id_list.append(nid)
                        fs.write(line)
            print(id_list)
            fs.close()
    print('finish unique')


path = './data/news/'
# ch_encode('./data/')
# rename_file(path)
unique_content(path)


