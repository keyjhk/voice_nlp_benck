import os

if __name__ == '__main__':
    name = 'A公馆 - 放漾（电影《反转人生》插曲）.mp3'
    files = filter(lambda fname: name in fname, [file for file in os.listdir('../media')])
    files = sorted(files, key=lambda x: int(x.split('part_')[-1]))
    with open('new file.mp3','wb') as f:
        for file in files:
            temp_file = open('../media/'+file,'rb')
            f.write(temp_file.read())
            temp_file.close()


