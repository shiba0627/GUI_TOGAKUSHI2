import tkinter as tk
import os
from PIL import Image, ImageTk
from enum import Enum
import time
from datetime import datetime


from base import ImageCache
HOVER_TIME = 0.3
BUTTON_SIZE_RATIO = 0.12#ボタンサイズ 画面横幅の何倍か
SETTING_SIZE_RATIO = 0.12
ARC_RADIUS = 30
DEFAULT_SPEED = 5#スピード初期値
MAX_SPEED = 10

PLUS = './img/plus.png'
PLUS_ATTENTION = './img/plus_attention.png'
PLUS_ACTIVE = './img/plus_active.png'
MINUS = './img/minus.png'
MINUS_ATTENTION = './img/minus_attention.png'
MINUS_ACTIVE = './img/minus_active.png'
START = './img/number/start.png'
START_ATTENTION = './img/number/start_attention.png'
RETRY = './img/number/retry.png'
RETRY_ATTENTION = './img/number/retry_attention.png'
SELECTED = './img/number/number_selected.png'
SETTING = './img/setting.png'
SETTING_ATTENTION = './img/setting_attention.png'
SETTING_ACTIVE = './img/setting_active.png'
ONE = './img/number/number_1.png'
ONE_ATTENTION = './img/number/number_1_attention.png'
TWO = './img/number/number_2.png'
TWO_ATTENTION = './img/number/number_2_attention.png'
THREE='./img/number/number_3.png'
THREE_ATTENTION = './img/number/number_3_attention.png'
FOUR='./img/number/number_4.png'
FOUR_ATTENTION = './img/number/number_4_attention.png'
FIVE='./img/number/number_5.png'
FIVE_ATTENTION = './img/number/number_5_attention.png'
SIX='./img/number/number_6.png'
SIX_ATTENTION = './img/number/number_6_attention.png'
SEVEN='./img/number/number_7.png'
SEVEN_ATTENTION = './img/number/number_7_attention.png'
EIGHT='./img/number/number_8.png'
EIGHT_ATTENTION = './img/number/number_8_attention.png'
NINE='./img/number/number_9.png'
NINE_ATTENTION = './img/number/number_9_attention.png'

class FrameName:
    READY = 'ready'
    GAME = 'game'
    RESULT = 'result'
    SETTING = 'setting'

class BaseButton:# ボタンのベースクラス
    def __init__(self, canvas, img_path, active_path, lock_path, attention_path, area, cmd, hover_time):
        self.canvas = canvas
        width = int(area[2] - area[0])
        height = int(area[3] - area[1])
        self.img = ImageCache.load(img_path, (width, height))
        self.img_lock = ImageCache.load(lock_path, (width, height))
        self.img_active = ImageCache.load(active_path, (width, height))
        self.img_attention = ImageCache.load(attention_path, (width, height))
        self.area = area
        self.stay_time = hover_time
        self.enter_time = None
        self.arc_id = None
        self.arc_radius = ARC_RADIUS
        self.cmd = cmd
        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")
        self.active = False

    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start = 90, extent=-angle, style = 'pieslice',
            outline = 'white', fill = 'black'
        )

    def set_attention(self):
        #ボタンをattentionにする
        self.canvas.itemconfig(self.image_id, image=self.img_attention)

    def set_nomal(self):
        #ボタンをnomalにする
        #各変数を初期化する
        self.enter_time=None
        self.active = False
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
        self.canvas.itemconfig(self.image_id, image=self.img)

    def set_active(self):
        #ボタンをactiveにする
        self.enter_time = None
        self.active = True
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
        self.canvas.itemconfig(self.image_id, image=self.img_active)

    def update(self, cursor_x, cursor_y):#カーソルのxy座標を受け取る
        if self.active:#アクティブなら、何もしない
            return None
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部なら
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y + 40, percent)
            if elapsed >= self.stay_time:
                print(f'{self.cmd}')
                self.set_active()
                return self.cmd
            else:
                self.set_attention()
        else:
            self.set_nomal()
        return None
class SpeedButton(BaseButton):
    def __init__(self, canvas, img_path, active_path, lock_path, attention_path, area, cmd, hover_time):
        super().__init__(canvas, img_path, active_path, lock_path, attention_path, area, cmd, hover_time)
    def update(self, cursor_x, cursor_y):#カーソルのxy座標を受け取る
        x1, y1, x2, y2 = self.area
        if self.active:#アクティブなら
            if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
                return None
            else:
                self.set_nomal()
                return None
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部なら
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y + 40, percent)
            if elapsed >= self.stay_time:
                print(f'{self.cmd}')
                self.set_active()
                return self.cmd
            else:
                self.set_attention()
        else:
            self.set_nomal()
        return None
class NumberButton:# ボタンのベースクラス
    def __init__(self, canvas, img_path,  attention_path, active_path, area, cmd, hover_time):
        self.canvas = canvas
        width = int(area[2] - area[0])
        height = int(area[3] - area[1])
        self.img = ImageCache.load(img_path, (width, height))
        self.img_active = ImageCache.load(active_path, (width, height))
        self.img_attention = ImageCache.load(attention_path, (width, height))
        self.area = area
        self.stay_time = hover_time
        self.enter_time = None
        self.arc_id = None
        self.arc_radius = ARC_RADIUS
        self.cmd = cmd
        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")
        self.active = False#選択済
        self.naxt = False#次が自分か？

    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start = 90, extent=-angle, style = 'pieslice',
            outline = 'white', fill = 'black'
        )

    def set_attention(self):
        #ボタンをattentionにする
        self.canvas.itemconfig(self.image_id, image=self.img_attention)

    def set_nomal(self):
        #ボタンをnomalにする
        #アクティブでなくす, 
        self.enter_time=None
        self.active = False
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
        self.canvas.itemconfig(self.image_id, image=self.img)

    def set_active(self):
        #ボタンをactiveにする, アークを消す
        self.enter_time = None
        self.active = True
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
        self.canvas.itemconfig(self.image_id, image=self.img_active)

    def update(self, cursor_x, cursor_y):#カーソルのxy座標を受け取る
        if self.active:#アクティブなら、何もしない
            return None
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部なら
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y + 40, percent)
            if elapsed >= self.stay_time:
                #print(f'{self.cmd}')
                self.set_active()
                return self.cmd
            else:
                self.set_attention()
        else:
            self.set_nomal()
        return None
class BaseFrame(tk.Frame):
    def __init__(self, master = None, app_instance = None):
        super().__init__(master)
        # Frameを画面ウィンドウいっぱいに敷く
        self.pack(fill=tk.BOTH, expand=True)#Frameをウィンドウ(master)いっぱいに配置

        #画面サイズを取得
        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()
        self.app = app_instance#フレーム遷移のコールバック
        self.canvas = tk.Canvas(self, width = self.width, height = self.height, bg="#202020",)
        self.canvas.pack(fill=tk.BOTH, expand=True)#canvasをmasterいっぱいに配置
        #self.canvas.pack()
        self.buttons = []
        self.last_active_obj = None

    def _calc_area(self, button_size_ratio, center_x_ratio, center_y_ratio):
        button_size_half = (button_size_ratio * self.width) / 2
        min_x = center_x_ratio * self.width - button_size_half
        max_x = center_x_ratio * self.width + button_size_half
        min_y = center_y_ratio * self.height - button_size_half
        max_y = center_y_ratio * self.height + button_size_half
        return (min_x, min_y, max_x, max_y)
    def check_cursor(self):
        x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        y = self.master.winfo_pointery() - self.master.winfo_rooty()

        #各ボタンにマウス位置を通知
        active_obj = None#新たにアクティブになったボタンのオブジェクト
        for button in self.buttons:
            active_cmd = button.update(x,y)
            if active_cmd == 'game':
                self.app.show_frame(FrameName.GAME)
            elif active_cmd == 're':
                self.app.show_frame(FrameName.READY)
            elif active_cmd == 'set':
                self.app.show_frame(FrameName.SETTING)

            if active_cmd is not None:#新たにアクティブになったボタンがあるなら
                active_obj = button#アクティブなボタンのオブジェクトを保存
        #全体のボタン状態の管理
        if active_obj:
            if self.last_active_obj and self.last_active_obj != active_obj:
                self.last_active_obj.set_nomal()
            self.last_active_obj = active_obj
        else:
            pass
        self.master.after(20, self.check_cursor)
class GameFrame(BaseFrame):# 操作画面
    def __init__(self, master = None, app_instance = None):
        super().__init__(master,  app_instance)
        self.next_number = 1
        self.max_number = 9
        self.canvas.config(bg="#ADD8E6")
        button_list = [
    (ONE,   ONE_ATTENTION,   SELECTED, 1/3, 1/2, 1),
    (TWO,   TWO_ATTENTION,   SELECTED, 1/2, 3/4, 2),
    (THREE, THREE_ATTENTION, SELECTED, 2/3, 1/2, 3),

    (FOUR,  FOUR_ATTENTION,  SELECTED, 1/3, 1/4, 4),
    (FIVE,  FIVE_ATTENTION,  SELECTED, 2/3, 1/4, 5),

    (SIX,   SIX_ATTENTION,   SELECTED, 1/2, 1/2, 6),

    (SEVEN, SEVEN_ATTENTION, SELECTED, 2/3, 3/4, 7),
    (EIGHT, EIGHT_ATTENTION, SELECTED, 1/2, 1/4, 8),

    (NINE,  NINE_ATTENTION,  SELECTED, 1/3, 3/4, 9),

]

        for img, attention, selected, center_x_ratio, center_y_ratio, cmd in button_list:
            area = self._calc_area(self.app.button_size_ratio, center_x_ratio,center_y_ratio)
            self.buttons.append(NumberButton(self.canvas, img, attention, selected, area, cmd, self.app.hover_time))
        self.check_cursor()

    def check_cursor(self):
        x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        y = self.master.winfo_pointery() - self.master.winfo_rooty()


        #各ボタンにマウス位置を通知
        active_obj = None#新たにアクティブになったボタンのオブジェクト
        for button in self.buttons:
            active_cmd = button.update(x,y)
            if isinstance(active_cmd, int)  and self.next_number < active_cmd :
                button.set_nomal()
            if self.next_number == active_cmd:
                self.next_number += 1
                print(self.next_number)
            if active_cmd == 'game':
                self.app.show_frame(FrameName.GAME)
            if active_cmd is not None:#新たにアクティブになったボタンがあるなら
                active_obj = button#アクティブなボタンのオブジェクトを保存
        if self.next_number == 10 and active_cmd == 9:
            self.app.end_time = time.time()
            self.app.show_frame(FrameName.RESULT)
        #全体のボタン状態の管理
        if self.next_number == 2:
            self.buttons[0].set_active()
        elif self.next_number == 3:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
        elif self.next_number == 4:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
            self.buttons[2].set_active()

        elif self.next_number == 5:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
            self.buttons[2].set_active()
            self.buttons[3].set_active()

        elif self.next_number == 6:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
            self.buttons[2].set_active()
            self.buttons[3].set_active()
            self.buttons[4].set_active()

        elif self.next_number == 7:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
            self.buttons[2].set_active()
            self.buttons[3].set_active()
            self.buttons[4].set_active()
            self.buttons[5].set_active()
        elif self.next_number == 8:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
            self.buttons[2].set_active()
            self.buttons[3].set_active()
            self.buttons[4].set_active()
            self.buttons[5].set_active()
            self.buttons[6].set_active()

        elif self.next_number == 9:
            self.buttons[0].set_active()
            self.buttons[1].set_active()
            self.buttons[2].set_active()
            self.buttons[3].set_active()
            self.buttons[4].set_active()
            self.buttons[5].set_active()
            self.buttons[6].set_active()
            self.buttons[7].set_active()
        self.master.after(20, self.check_cursor)
class ReadyFrame(BaseFrame):# 準備画面
    def __init__(self, master = None, app_instance = None):
        super().__init__(master,  app_instance)
        self.canvas.config(bg="#B8B7DF")
        button_list = [
            (START, START_ATTENTION, SELECTED,  4/5, 1/2, 'game'),
            (SETTING, SETTING_ATTENTION, SELECTED, 1/2, 1/2, 'set')]
        for img, attention, selected, center_x_ratio, center_y_ratio, cmd in button_list:
            area = self._calc_area(0.2, center_x_ratio,center_y_ratio)
            self.buttons.append(NumberButton(self.canvas, img, attention, selected, area, cmd, self.app.hover_time))
        self.check_cursor()
class ResultFrame(BaseFrame):
    def __init__(self, master = None, app_instance = None):
        super().__init__(master,  app_instance)
        self.canvas.config(bg="#DFB7B7")
        cx = self.width * 0.35
        cy = self.height * 1/3
        t=self.app.end_time - self.app.start_time
        self.canvas.create_text(cx, cy - 100, text=f"クリアタイム：{t:.0f}秒！！", font=("Arial", 90))
        button_list = [
            (RETRY, RETRY_ATTENTION, SELECTED,  1/5, 1/2, 're'),]
        for img, attention, selected, center_x_ratio, center_y_ratio, cmd in button_list:
            area = self._calc_area(0.2, center_x_ratio,center_y_ratio)
            self.buttons.append(NumberButton(self.canvas, img, attention, selected, area, cmd, self.app.hover_time))
        now = datetime.now()
        now_micro = now.strftime('%Y%m%d_%H%M%S')
        file_name = f'output/number3_result_{now_micro}.txt'
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(f"n3.py\n")
                    f.write(f"数字消し\n")
                    f.write(f"{t}秒\n")
                    f.write(f'滞留時間{self.app.hover_time}秒')
        except IOError as e:
            print(e)
        self.check_cursor()

class SettingFrame(BaseFrame):
    def __init__(self, master = None, app_instance = None):
        super().__init__(master, app_instance)
        self.canvas.config(bg="#98FB98")
        
        # === 速度表示テキスト ===
        cx = self.width * 2/4
        cy = self.height * 1/2
        self.canvas.create_text(cx, cy - 130, text="みるじかん", font=("Arial", 90))
        # テキストIDを保存して後で書き換えられるようにする
        self.speed_text_id = self.canvas.create_text(cx, cy, text=f'{self.app.hover_time:.1f}秒', font=("Arial", 90, "bold"))

        button_list = [
            (PLUS, PLUS_ACTIVE, '_', PLUS_ATTENTION, 1/4, 3/6, '+'),
            (MINUS, MINUS_ACTIVE, '_', MINUS_ATTENTION, 3/4, 3/6, '-'),
        ]
        for img, active, lock, attention, center_x_ratio, center_y_ratio, cmd in button_list:
            area = self._calc_area(BUTTON_SIZE_RATIO, center_x_ratio,center_y_ratio)
            self.buttons.append(SpeedButton(self.canvas, img, active, lock, attention, area, cmd, self.app.hover_time))
        
        #設定ボタンについて
        area = self._calc_area(SETTING_SIZE_RATIO, 9/10, 2/10)
        self.buttons.append(NumberButton(self.canvas, SETTING, SETTING_ACTIVE,SETTING_ATTENTION, area, 'set', self.app.hover_time))
        self.check_cursor()

    def update_speed_display(self):
        self.canvas.itemconfig(self.speed_text_id, text=f'{self.app.hover_time:.1f}秒')

    def check_cursor(self):
        x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        y = self.master.winfo_pointery() - self.master.winfo_rooty()

        #各ボタンにマウス位置を通知
        active_obj = None#新たにアクティブになったボタンのオブジェクト
        for button in self.buttons:
            active_cmd = button.update(x,y)#今フレームでアクティブになったボタン
            if active_cmd == 'set':
                self.app.show_frame(FrameName.READY)#controlに遷移
                return
            elif active_cmd == '+':
                if self.app.hover_time < 5:
                    self.app.hover_time += 0.1
                    self.update_speed_display()
            elif active_cmd == '-':
                if self.app.hover_time > 0.12:
                    self.app.hover_time -= 0.1
                    self.update_speed_display()

            if active_cmd is not None:#新たにアクティブになったボタンがあるなら
                active_obj = button#アクティブなボタンのオブジェクトを保存
        #全体のボタン状態の管理
        if active_obj:#新たにアクティブになったボタンがあるなら
            if self.last_active_obj and self.last_active_obj != active_obj:
                self.last_active_obj.set_nomal()
            self.last_active_obj = active_obj
        else:
            pass
        self.master.after(20, self.check_cursor)
class mainApp:
    def __init__(self):
        #全体で共有するデータを定義
        self.root = tk.Tk()
        self.root.title('eye controll game')
        self.root.state("zoomed")
        self.current_frame = None#現在表示中のフレーム
        self.start_time = time.time()
        self.end_time = None
        self.hover_time = HOVER_TIME#滞留時間
        self.button_size_ratio = BUTTON_SIZE_RATIO
        self.show_frame(FrameName.READY)

    def show_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.destroy()
        if frame_name == FrameName.READY:
            self.current_frame = ReadyFrame(self.root, self)
        elif frame_name == FrameName.GAME:
            self.start_time = time.time()
            self.current_frame = GameFrame(self.root, self)
        elif frame_name == FrameName.RESULT:
            self.current_frame = ResultFrame(self.root, self)
        elif frame_name == FrameName.SETTING:
            self.current_frame = SettingFrame(self.root, self)
    def run(self):
        self.root.mainloop()

def main():
    app = mainApp()
    app.run()

if __name__ == '__main__':
    main()