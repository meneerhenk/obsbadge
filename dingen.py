# NEEDED: https://github.com/Palakis/obs-websocket on your OBS install.
HOSTURL = "ws://192.168.1.66:4444"
import display, keypad, wifi, json
import uwebsockets.client
studiomode = False
transitions = []
curtrans = ""
scenes = []
curscenes = ""
blink = False
toscene = None

on = 0xFF0000
ledtrans = 0xFF0000
ledcurtrans = 0xFFFF00
ledscene = 0xFF0000
ledpreview = 0x00FF00
off = 0x000000

def on_key(key_index, pressed):
    x, y = key_index % 4, int(key_index / 4)
    if pressed:
        if y == 0:
            if x < len(transitions):
                wscl.send(json.dumps({'message-id':'3', 'request-type':'SetCurrentTransition', 'transition-name': transitions[x]}))
        else:
            scenum = y*4+x-4
            if scenum < len(scenes):
                wscl.send(json.dumps({'message-id':'3', 'request-type':'SetCurrentScene', 'scene-name': scenes[scenum]}))
    else:
        pass

def gettransitions():
    global transitions, curtrans
    wscl.send(json.dumps({'message-id':'3', 'request-type':'GetTransitionList'}))
    trans = json.loads(wscl.recv())
    transitions = [x['name'] for x in trans['transitions']][0:4]
    curtrans = trans['current-transition']

def getscenes():
    global scenes, curscene
    wscl.send(json.dumps({'message-id':'4', 'request-type':'GetSceneList'}))
    sces = json.loads(wscl.recv())
    scenes = [x['name'] for x in sces['scenes']][0:12]
    curscene = sces['current-scene']

def paintbuttons():
    global transitions,scenes,curtrans,curscene
    y = 0
    for x in range(0,len(transitions)):
        if curtrans == transitions[x]:
            display.drawPixel(x, y, 0x00FF00)
        else:
            display.drawPixel(x, y, 0xFF0000)
    for x in range(len(transitions),4):
        display.drawPixel(x, y, 0x00000)
    for num in range(0,len(scenes)):
        x, y = num % 4, int(num / 4)+1
        if curscene == scenes[num]:
            display.drawPixel(x, y, 0x0000FF)
        else:
            display.drawPixel(x, y, 0xFF8C00)
    display.flush()


wifi.connect()
while not wifi.status():
    pass
wscl = uwebsockets.client.connect(HOSTURL)
requestpayload = {'message-id':'1', 'request-type':'GetAuthRequired'}
wscl.send(json.dumps(requestpayload))
needauth = json.loads(wscl.recv())
if needauth['authRequired'] == False:
    print("No auth.. good...")
    wscl.send(json.dumps({'message-id':'2', 'request-type':'GetStudioModeStatus'}))
    studiomode = json.loads(wscl.recv())['studio-mode']
    gettransitions()
    print("Loaded",len(transitions))
    getscenes()
    print("Loaded",len(scenes))
    wscl.sock.settimeout(0.1)
    paintbuttons()
    keypad.add_handler(on_key)

    while True:
        try:
            msg = json.loads(wscl.recv())
            if 'update-type' in msg:
                if msg['update-type'] == 'TransitionBegin':
                    blink = 1
                    toscene = msg['to-scene']
                elif msg['update-type'] == 'TransitionEnd':
                    blink = False
                    paintbuttons()
                elif msg['update-type'] == 'PreviewSceneChanged':
                    pass
                elif msg['update-type'] == 'SwitchScenes':
                    curscene = msg['scene-name']
                    paintbuttons()
                elif msg['update-type'] == 'SwitchTransition':
                    curtrans = msg['transition-name']
                    paintbuttons()
                elif msg['update-type'] == 'TransitionListChanged':
                    gettransitions()
                    paintbuttons()
            print(msg)
        except OSError:
            pass
        if blink:
            blink += 1
            if blink == 2:
                scenenum = scenes.index(toscene)
                x, y = scenenum % 4, int(scenenum / 4)
                display.drawPixel(x, y+1, 0x0000FF)
                display.flush()
            elif blink == 4:
                scenenum = scenes.index(toscene)
                x, y = scenenum % 4, int(scenenum / 4)
                display.drawPixel(x, y+1, 0xFF8C00)
                display.flush()
            elif blink == 6:
                blink = 1
  
print("Error")

