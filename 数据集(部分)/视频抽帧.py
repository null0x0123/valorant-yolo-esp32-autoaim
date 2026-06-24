import  cv2
import matplotlib.pyplot as plt

video_list = ["Valorant 2026.05.26 - 14.22.23.17.mp4",
              "Valorant 2026.05.26 - 14.22.14.16.mp4",
              "Valorant 2026.05.26 - 14.20.02.15.mp4",
              "Valorant 2026.05.26 - 14.16.46.14.mp4",
              "Valorant 2026.05.26 - 14.14.15.13.mp4",
              "Valorant 2026.05.26 - 14.11.41.12.mp4",
              "Valorant 2026.05.26 - 14.09.30.11.mp4",
              "Valorant 2026.05.26 - 14.06.51.10.mp4",
              "Valorant 2026.05.26 - 14.05.06.09.mp4",
              "Valorant 2026.05.26 - 14.03.55.08.mp4",
              "Valorant 2026.05.26 - 14.01.11.07.mp4",
              "Valorant 2026.05.26 - 13.58.18.06.mp4",
              "Valorant 2026.05.26 - 13.55.48.05.mp4",
              "Valorant 2026.05.26 - 13.54.09.04.mp4",
              "Valorant 2026.05.26 - 13.43.20.02.mp4",
              "Valorant 2026.05.26 - 13.38.10.01.mp4"]

video_count = 0

for i in video_list:

    video_count = video_count + 1

    video_path = r"视频/" + i

    video = cv2.VideoCapture(video_path)

    img_count = 1
    save_step = 30
    num = 0

    while True:
        ret,frame = video.read()
        if not ret:
            break
        if num % save_step == 0:
            cv2.imencode('.png', frame)[1].tofile(f"图片/{video_count}_{img_count}.png")
            img_count = img_count + 1
        num = num + 1
    video.release()