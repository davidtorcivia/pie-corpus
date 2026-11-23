# Runs in the Colab kernel (colab exec) and keeps it BUSY until the run is done: Colab reclaims a VM whose kernel is
# idle, and the trainer itself runs outside the kernel (nohup over ssh).
import os, time
while not os.path.exists('/content/w/DONE'):
    time.sleep(300); print(time.strftime('%H:%M'), flush=True)
print('DONE', flush=True)
