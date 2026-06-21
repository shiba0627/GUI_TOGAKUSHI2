
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import time
import threading
import socket
import json
import cv2
import numpy as np
from datetime import datetime
# ==== 定数設定 ====
BUTTON_SIZE = 250
HOVER_TIME  = 0.3
ARC_RADIUS  = 30

#SERVER_HOST = '192.168.1.102'#有線
SERVER_HOST = '192.168.5.3'#無線(TOGAKUSHI2)  

# ポートを制御用と画像用に分離
CONTROL_PORT = 12345 # 制御・状態
IMAGE_PORT   = 12346 # 画像

# ==== 画像パス ====
IMG_DIR = './img'
FORWARD, BACK, CW, CCW, STOP = [os.path.join(IMG_DIR, name) for name in
    ['forward.png', 'back.png', 'cw.png', 'ccw.png', 'stop.png']]
FORWARD_ACTIVE, BACK_ACTIVE, CW_ACTIVE, CCW_ACTIVE, STOP_ACTIVE = [p.replace('.png', '_active.png') for p in [FORWARD, BACK, CW, CCW, STOP]]
FORWARD_ATTENTION, BACK_ATTENTION, CW_ATTENTION, CCW_ATTENTION, STOP_ATTENTION = [p.replace('.png', '_attention.png') for p in [FORWARD, BACK, CW, CCW, STOP]]
FORWARD_LOCK, BACK_LOCK, CW_LOCK, CCW_LOCK, STOP_LOCK = [p.replace('.png', '_lock.png') for p in [FORWARD, BACK, CW, CCW, STOP]]

# ==== ボタンクラス ====
class makeButton:
    def __init__(self, canvas, img_path, dark_path, lock_path, attention_path, area, cmd):
        self.canvas = canvas
        width = int(area[2] - area[0])
        height = int(area[3] - area[1])
        self.img         = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_dark    = ImageTk.PhotoImage(Image.open(dark_path).resize((width, height)))
        self.img_lock    = ImageTk.PhotoImage(Image.open(lock_path).resize((width, height)))
        self.img_attention = ImageTk.PhotoImage(Image.open(attention_path).resize((width, height)))
        self.area = area
        self.stay_time  = HOVER_TIME#滞留時間
        self.enter_time = None
        self.clicked    = False
        self.locked     = False # ロック状態を管理するフラグ
        self.arc_id     = None
        self.arc_radius = ARC_RADIUS
        self.cmd        = cmd
        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")

    def lock(self):
        """ボタンをロック状態にする"""
        if not self.locked:
            self.locked = True
            self.reset() # 滞留中などの状態をクリア
            self.canvas.itemconfig(self.image_id, image=self.img_lock)

    def unlock(self):
        """ボタンのロックを解除する"""
        if self.locked:
            self.locked = False
            self.reset()

    def reset(self):
        self.enter_time = None
        self.clicked    = False
        # ロック中でなければ通常の画像に戻す
        if not self.locked:
            self.canvas.itemconfig(self.image_id, image=self.img)
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None

    def set_dark_state(self):
        self.enter_time = None
        self.clicked = True
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
        self.canvas.itemconfig(self.image_id, image=self.img_dark)

    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start=90, extent=-angle, style='pieslice',
            outline='white', fill='black'
        )

    def update(self, cursor_x, cursor_y):
        # ロック中、またはクリック済みなら何もしない
        if self.locked or self.clicked:
            return None
            
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y, percent)
            self.canvas.itemconfig(self.image_id, image=self.img_attention)
            if elapsed >= self.stay_time:
                self.set_dark_state()
                return self.cmd
        else:
            self.reset()
        return None

# ==== GUIアプリ ====
class GUIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width  = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.log=[]
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)#終了を検出
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)

        # 背景画像表示用のキャンバスアイテム
        self.tk_image = None # ガベージコレクション防止用
        self.latest_cv_frame = None # OpenCVでデコードした最新の画像
        self.image_on_canvas = self.canvas.create_image(
            self.width / 2, self.height / 2, anchor='center'
        )

        button_list = [
            (FORWARD, FORWARD_ACTIVE, FORWARD_LOCK, FORWARD_ATTENTION, 2/4, 1/6, 'w'),
            (CCW, CCW_ACTIVE, CCW_LOCK, CCW_ATTENTION, 1/4, 3/6, 'a'),
            (CW, CW_ACTIVE, CW_LOCK, CW_ATTENTION, 3/4, 3/6, 'd'),
            (STOP, STOP_ACTIVE, STOP_LOCK, STOP_ATTENTION, 2/4, 3/6, 's'),
            (BACK, BACK_ACTIVE, BACK_LOCK, BACK_ATTENTION, 2/4, 5/6, 'z'),
        ]
        
        # ボタンをコマンド名で管理
        self.button_map = {}
        for img, dark, lock, attention, cx, cy, cmd in button_list:
            area = self.calc_area(cx * self.width, cy * self.height)
            button = makeButton(self.canvas, img, dark, lock, attention, area, cmd)
            self.button_map[cmd] = button

        # 初期状態をSTOPに設定
        self.last_activated_button = self.button_map['s']
        self.last_activated_button.set_dark_state()
        self.last_sent_data = 's'

        # 制御用UDPソケット
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_sock.settimeout(0.1)

        self.mode = 'USER'
        
        # 制御データ受信用スレッド起動
        threading.Thread(target=self.receive_control_data, daemon=True).start()
        
        # 画像受信用スレッド起動
        threading.Thread(target=self.receive_image_data, daemon=True).start()

        self.check_cursor()

    def calc_area(self, cx, cy):
        half = BUTTON_SIZE / 2
        return (cx - half, cy - half, cx + half, cy + half)
    def logger(self, cmd):
        if cmd is None:
            return 
        now = datetime.now()
        self.log.append(str(now)+' ' +cmd)
    
    def update_lock_status(self, locked_cmds):
        """ボタンのロック状態をGUIに反映"""
        for cmd, button in self.button_map.items():
            if cmd in locked_cmds:
                button.lock()
            else:
                button.unlock()
        
        # 現在アクティブなボタンがロックされたら、STOP
        if self.last_activated_button and self.last_activated_button.locked:
            self.last_activated_button = self.button_map['s']
            self.last_activated_button.set_dark_state()
            self.last_sent_data = 's'


    def send_command(self, cmd):
        """Joy相当のデータをUDP送信"""
        if cmd == 'w':   msg = "0.0, 0.11"
        elif cmd == 'z': msg = "0.0, -0.15"
        elif cmd == 'a': msg = "0.18, 0.0"
        elif cmd == 'd': msg = "-0.18, 0.0"
        else:            msg = "0.0, 0.0"

        try:
            if self.mode == 'USER':
                # 制御ポートに送信
                self.control_sock.sendto(msg.encode('utf-8'), (SERVER_HOST, CONTROL_PORT))
            elif self.mode == 'GAME':
                #  制御ポートに送信
                self.control_sock.sendto(msg.encode('utf-8'), (SERVER_HOST, CONTROL_PORT))
            else:
                zero = "0.0, 0.0"
                #  制御ポートに送信
                self.control_sock.sendto(zero.encode('utf-8'), (SERVER_HOST, CONTROL_PORT))
        except Exception as e:
            print(f"[送信エラー] {e}")

    def receive_control_data(self):
        """サーバーからの制御データ(状態・障害物)受信 (旧 receive_data)"""
        while True:
            try:
                # 制御ソケットから受信
                data, _ = self.control_sock.recvfrom(1024)
                # 受信データがシングルクォートの場合があるので、JSON用にダブルクォートに置換
                msg_str = data.decode('utf-8').replace("'", '"')

                try:
                    # obstacle_data に {'obstacle_front': 0, ...} のようなデータが入る
                    obstacle_data = json.loads(msg_str)
                    print(obstacle_data)
                    # 障害物データからロックするコマンドのリストを動的に作成
                    commands_to_lock = []
                    if obstacle_data.get('obstacle_front') == 1:
                        commands_to_lock.append('w') # 前進ボタン
                    if obstacle_data.get('obstacle_back') == 1:
                        commands_to_lock.append('z') # 後退ボタン
                    if obstacle_data.get('obstacle_left') == 1:
                        commands_to_lock.append('a') # 左回転(CCW)ボタン
                    if obstacle_data.get('obstacle_right') == 1:
                        commands_to_lock.append('d') # 右回転(CW)ボタン
                    mode = obstacle_data.get('robot_state')
                    if mode == 'USER':
                        self.mode = 'USER'
                    elif mode == 'GAME':
                        self.mode = 'GAME'
                    else:
                        self.mode = 'HELPER'
                    
                    # 構築したコマンドリストを使ってGUIの更新を依頼
                    self.root.after(0, self.update_lock_status, commands_to_lock)

                except (json.JSONDecodeError, TypeError):
                    # JSONとして解釈できない場合は、そのままログに表示
                    print(f"[UDP応答] {data.decode('utf-8')}")

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[制御受信エラー] {e}")

    def receive_image_data(self):
        """サーバーからの画像データ受信"""
        
        image_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 画像ポートで待ち受け
        image_sock.bind(('0.0.0.0', IMAGE_PORT)) 
        image_sock.settimeout(1.0) # 1秒タイムアウト
        
        while True:
            try:
                # 65536 バイトのバッファでデータを受信
                data, _ = image_sock.recvfrom(65536)
                
                # 受信したバイトデータをnumpy配列に変換
                np_arr = np.frombuffer(data, dtype=np.uint8)
                
                # numpy配列をOpenCVの画像形式(BGR)にデコード
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # デコード成功したら最新のフレームとして保持
                    self.latest_cv_frame = frame
                    
            except socket.timeout:
                # タイムアウトは正常（画像が来ていないだけ）
                continue
            except Exception as e:
                print(f"[画像受信エラー] {e}")


    def update_image_display(self):
        """キャンバスの背景画像を更新する"""
        if self.latest_cv_frame is None:
            return

        try:
            # OpenCV(BGR) -> PIL(RGB)
            cv_rgb = cv2.cvtColor(self.latest_cv_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(cv_rgb)

            # キャンバスサイズに合うようにリサイズ (アスペクト比維持)
            img_w, img_h = pil_img.size
            ratio = min(self.width / img_w, self.height / img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
            
            pil_img_resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # PIL -> PhotoImage
            # ★ self.tk_image に保持しないとガベージコレクションで消える
            self.tk_image = ImageTk.PhotoImage(image=pil_img_resized)
            
            # キャンバスの画像を更新
            self.canvas.itemconfig(self.image_on_canvas, image=self.tk_image)
            # 画像をボタンの背面に移動
            self.canvas.lower(self.image_on_canvas)

        except Exception as e:
            print(f"[画像表示エラー] {e}")


    def check_cursor(self):
        """マウス位置の定期監視"""
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        
        activated_button_this_frame = None
        for button in self.button_map.values():
            cmd = button.update(x, y)
            if cmd:
                activated_button_this_frame = button
                self.last_sent_data = cmd
                self.logger(cmd)

        if activated_button_this_frame and self.last_activated_button != activated_button_this_frame:
            if self.last_activated_button:
                self.last_activated_button.reset()
            self.last_activated_button = activated_button_this_frame

        # 常に self.last_sent_data に基づいてコマンドを送信
        #threading.Thread(target=self.send_command, args=(self.last_sent_data,), daemon=True).start()
        self.send_command(self.last_sent_data)
        # 画像表示を更新
        self.update_image_display()

        #self.root.after(33, self.check_cursor) # 約30fps
        self.root.after(50, self.check_cursor)
    def on_close(self):
        self.save_log()
        self.root.destroy()
    def save_log(self):
        if not self.log:
            return

        log_dir = "output"
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(log_dir, f"mainLOG_{timestamp}.txt")

        with open(filepath, "w", encoding="utf-8") as f:
            for line in self.log:
                f.write(line + "\n")

    def run(self):
        self.root.mainloop()

# ==== メイン ====
if __name__ == '__main__':
    GUIApp().run()