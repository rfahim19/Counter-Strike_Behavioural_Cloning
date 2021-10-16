import numpy as np
import cv2
import time


data = np.load(
    'D:\Work\\train-demo\\training_data_2\\training_data-0.npy', allow_pickle=True)


# for image in d:
#     print(image.shape)
#     cv2.imshow("OpenCV/Numpy normal", image)
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break
#     time.sleep(.1)

datas = []

for d in data:
    print(d.shape)
    datas.append(d)

print(datas)