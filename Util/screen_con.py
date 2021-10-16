import pyautogui, sys
print('Press Ctrl-C to quit.')
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    print('\n')



pyautogui.moveTo(563, 745)
pyautogui.click()
pyautogui.press('enter')
pyautogui.press(' ')

# pyautogui.moveTo(39, 43)  # moves mouse to X of 100, Y of 200.
# pyautogui.move(0, 50)       # move the mouse down 50 pixels.
# pyautogui.move(-30, 0)      # move the mouse left 30 pixels.
# pyautogui.move(-30, None)   # move the mouse left 30 pixels.
# pyautogui.click()