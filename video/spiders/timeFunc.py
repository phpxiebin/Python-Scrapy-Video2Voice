import os,re

def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read().strip()
    r.close()
    return text

def getSeconds(url):
    #url = "http://stream5.iqilu.com/vod_bag_2016//2018/04/25/66862F34979F4f919852A993BB0D4F7E/66862F34979F4f919852A993BB0D4F7E_H264_mp4_500K.mp4"
    cmd = "ffmpeg -i "+url+" 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//"
    text = execCmd(cmd)
    search_group = re.search('(\d+):(\d+):(\d+)', text)

    if search_group:
        time_hours = int(search_group.group(1))
        time_minutes = int(search_group.group(2))
        time_seconds = int(search_group.group(3))
        all_count_seconds = time_hours * 60 * 60 + time_minutes * 60 + time_seconds
        return all_count_seconds
