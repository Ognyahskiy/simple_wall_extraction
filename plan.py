import os
import argparse
import numpy as np
import cv2
import json

def extract_walls(img):
    kernel=np.ones((5,5))
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img=cv2.GaussianBlur(img,(5,5),1)
    ret,img=cv2.threshold(img,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    img = cv2.bitwise_not(img)
    img=cv2.erode(img,kernel,iterations=2)
    img=cv2.dilate(img,kernel,iterations=2)
    return img

def save_walls(img,img_name):
    walls=[]
    wid=1
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area>100:
            peri = cv2.arcLength(cnt, True)
            C=4*np.pi*area/(peri*peri)
            if C<0.8:
                cnt = cnt.reshape(-1, 2).tolist()
                walls.append({"id":f"w{wid}","points":cnt})
                wid+=1
    return {"meta":{"source":img_name},"walls":walls}

def save_json(data, out_path):
    os.makedirs(os.path.dirname(out_path),exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f)

def draw_walls(img,json_file):
    out=img.copy()
    for w in json_file.get("walls", []):
        pts = np.asarray(w["points"], dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(out, [pts], isClosed=True, color=(0,255,0), thickness=2)
        if True and len(pts) > 0:
            x, y = pts[0, 0]
            cv2.putText(out, w["id"],(int(x), int(y)),cv2.FONT_HERSHEY_SIMPLEX,0.8, (255, 0, 0), 1, cv2.LINE_AA)
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img_path", type=str, required=True, help="Путь изображения")
    parser.add_argument("--json_path", type=str, required=True, help="Путь записи json файла")
    parser.add_argument("--overlay_path", type=str, help="Путь для фото с наложением стен")
    args = parser.parse_args()
    img=cv2.imread(args.img_path)
    frame=extract_walls(img)
    data=save_walls(frame,args.img_path)
    save_json(data,args.json_path)
    if args.overlay_path:
        with open(args.json_path, "r") as f:
            data = json.load(f)
        overlay=draw_walls(img,data)
        cv2.imwrite(args.overlay_path, overlay)

if __name__=="__main__":
    main()
