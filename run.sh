cd /home/vvn1/jarod_display
git reset --hard
git pull
sudo python app.py --led-cols=64  --led-no-hardware-pulse=1 -m  adafruit-hat-pwm --led-slowdown-gpio=4
