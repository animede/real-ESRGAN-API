import argparse
import cv2
import glob
import os
from datetime import datetime
import pickle
import requests
import numpy as np
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='inputs', help='Input image or folder')
    parser.add_argument('-o', '--output', type=str, default='results', help='Output folder')
    parser.add_argument('-s', '--outscale', type=str, default=4, help='The final upsampling scale of the image')
    parser.add_argument( '-t', '--test', type=bool, default=False, help='excecute test PG if True')
    parser.add_argument("--host", type=str,  default="0.0.0.0",  help="サービスを提供するip アドレスを指定。")
    parser.add_argument("--port", type=int,  default=50008,    help="サービスを提供するポートを指定。")
    args = parser.parse_args()

    host="0.0.0.0"    # サーバーIPアドレス定義
    port=8008          # サーバー待ち受けポート番号定義
    url="http://" + host + ":" + str(port) + "/resr_upscal/"
    
    #+++++++++++++++   test    +++++++++++++++++++
    if args.test==True:
        if os.path.isfile(args.input):
            paths = [args.input]
        else:
            paths = sorted(glob.glob(os.path.join(args.input, '*')))
        img_list=[]
        for idx, path in enumerate(paths):
            imgname, extension = os.path.splitext(os.path.basename(path))
            print('Testing', idx, imgname)
            cv_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            img_list.append(cv_img)
        start_time = datetime.now()
        count=len(img_list)
        for i in range(0,count):
            img=img_list[i]
            #print("Send_time=",datetime.now())
            start_now=time.time()
            output = up_scale(url, img , args.outscale) # <<<<<<<<<<<<<<<<<<   up_scale(url , img ,  scale):
            #print("Recive_time=",datetime.now())
            print((time.time()-start_now)*1000,"mS")

            if len(img.shape) == 3 and img.shape[2] == 4:
                extension = '.png'
            else:
                extension = '.jpg'
            save_path = args.output + "/" + str(i)+extension
            print("---",save_path)
            cv2.imwrite(save_path, output) #if files are require #ファイルへ書き出しをすると遅くなります。
        print("start_time=",start_time)
        print("end_time=",datetime.now())

# ++++++++++++++  up scale ++++++++++++++++
def up_scale(url , img ,  scale=4):
    #_, img_encoded = cv2.imencode('.jpg', img)
    images_data = pickle.dumps(img, 5) 
    files = {"image": ("img.dat",  images_data, "application/octet-stream")}
    data = {"scale": scale}
    response = requests.post(url, files=files,data=data)
    
    all_data =response.content
    up_data = (pickle.loads(all_data))#元の形式にpickle.loadsで復元
    return up_data #形式はimg_mode指定の通り

if __name__ == '__main__':
    main()
