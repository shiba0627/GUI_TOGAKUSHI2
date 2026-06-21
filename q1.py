import tkinter as tk
import time
from datetime import datetime
from base import ImageCache

#パラメータ
HOVER_TIME = 0.4
BUTTON_SIZE_RATIO = 0.12#ボタンサイズ 画面横幅の何倍か
SETTING_SIZE_RATIO = 0.12
ARC_RADIUS = 30
DEFAULT_SPEED = 5#スピード初期値
MAX_SPEED = 10

#ボタン画像
BAD = './img/questionnaire/bad.png'
BAD_ATTENTION = './img/questionnaire/bad_attention.png'
BAD_ACTIVE = './img/questionnaire/bad_active.png'
SOSO = './img/questionnaire/soso.png'
SOSO_ATTENTION = './img/questionnaire/soso_attention.png'
SOSO_ACTIVE = './img/questionnaire/soso_active.png'
GOOD = './img/questionnaire/good.png'
GOOD_ATTENTION = './img/questionnaire/good_attention.png'
GOOD_ACTIVE = './img/questionnaire/good_active.png'

NEXT = './img/questionnaire/next.png'
NEXT_ATTENTION = './img/questionnaire/next_attention.png'
BACK = './img/questionnaire/return.png'
BACK_ATTENTION = './img/questionnaire/return_attention.png'

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

class FrameName:
    READY = 'ready'
    QUESTION = 'question'
    ANSWER = 'answer'
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
    def __init__(self, canvas, img_path, attention_path, active_path, area, cmd, hover_time):
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
            if active_cmd == 'question':
                self.app.show_frame(FrameName.QUESTION)
            elif active_cmd == 'ready':
                self.app.show_frame(FrameName.READY)
            elif active_cmd == 'setting':
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

class ReadyFrame(BaseFrame):# 準備画面
    def __init__(self, master = None, app_instance = None):
        super().__init__(master,  app_instance)
        self.canvas.config(bg="#B8B7DF")
        cx = self.width * 0.5
        cy = self.height * 1/4
        self.canvas.create_text(cx, cy, text=f"質問は5個です。\n気軽に答えてください！", font=("Arial", 90))
        button_list = [
            (START, START_ATTENTION, SELECTED,  4/5, 2/3, 'question'),
            (SETTING, SETTING_ATTENTION, SELECTED, 1/2, 2/3, 'setting')]
        for img, attention, selected, center_x_ratio, center_y_ratio, cmd in button_list:
            area = self._calc_area(0.2, center_x_ratio,center_y_ratio)
            self.buttons.append(NumberButton(self.canvas, img, attention, selected, area, cmd, self.app.hover_time))
        self.check_cursor()

class ResultFrame(BaseFrame):
    def __init__(self, master = None, app_instance = None):
        super().__init__(master,  app_instance)
        self.canvas.config(bg="#DFB7B7")
        cx = self.width * 0.5
        cy = self.height * 1/3
        t=self.app.end_time - self.app.start_time
        self.canvas.create_text(cx, cy - 10, text=f"ありがとうございました！", font=("Arial", 90))
        now = datetime.now()
        now_micro = now.strftime('%Y%m%d_%H%M%S')
        file_name = f'output/question_result_{now_micro}.txt'
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(f"{t}秒\n")
                    f.write(f'滞留時間{self.app.hover_time}秒')
                    # 回答内容
                    f.write("【回答結果】\n")
                    for question, answer in zip(self.app.questions, self.app.answers):
                        f.write(f"質問: {question}\n")
                        f.write(f"回答: {answer}\n")
                        f.write("\n")
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
        self.buttons.append(NumberButton(self.canvas, SETTING, SETTING_ACTIVE,SETTING_ATTENTION, area, 'setting', self.app.hover_time))
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
            if active_cmd == 'setting':
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
class QuestionFrame(BaseFrame):
    
    def __init__(self, master=None, app_instance=None):
        super().__init__(master, app_instance)
        self.canvas.config(bg="#EFEFEF")

        q_idx = self.app.question_index
        question_text = self.app.questions[q_idx]

        # === 設問表示 ===
        self.canvas.create_text(
            self.width / 2,
            self.height * 0.15,
            text=question_text,
            font=("Arial", 60),
            width=self.width * 0.8
        )

        # === 次へ、戻るボタン ===

        button_list = [
            (NEXT, NEXT_ATTENTION, NEXT_ATTENTION, 1/4, 3/4, 'NEXT'),
        ]


        for img, active, attention, cx, cy, cmd in button_list:
            area = self._calc_area(0.15, cx, cy)
            self.buttons.append(
                BaseButton(
                    self.canvas,
                    img,
                    active,
                    img,          # lock 未使用
                    attention,
                    area,
                    cmd,
                    self.app.hover_time
                )
            )

        self.check_cursor()

    def check_cursor(self):
        x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        y = self.master.winfo_pointery() - self.master.winfo_rooty()

        for button in self.buttons:
            active_cmd = button.update(x, y)
            if active_cmd == 'NEXT':
                self.on_answer(active_cmd)
                return

        self.master.after(20, self.check_cursor)

    def on_answer(self, answer):
        # 回答画面へ
        next_frame = FrameName.ANSWER
        self.app.show_frame(next_frame)
class AnswerFrame(BaseFrame):
    def __init__(self, master=None, app_instance=None):
        super().__init__(master, app_instance)
        self.canvas.config(bg="#EFEFEF")
        q_idx = self.app.question_index
        question_text = self.app.questions[q_idx]
        
        self.selected_cmd = None  # ★現在選択されている回答を保存する変数

        # === 回答ボタン ===
        button_list = [
            (BAD,  BAD_ACTIVE,  BAD_ATTENTION, 3/4, 2/6, 'BAD'),
            (SOSO, SOSO_ACTIVE, SOSO_ATTENTION, 2/4, 2/6, 'SOSO'),
            (GOOD, GOOD_ACTIVE, GOOD_ATTENTION, 1/4, 2/6, 'GOOD'),
            (NEXT, NEXT_ATTENTION, NEXT_ATTENTION, 3/4, 3/4, 'NEXT'), # NEXTボタン
        ]

        for img, active, attention, cx, cy, cmd in button_list:
            area = self._calc_area(0.15, cx, cy)
            self.buttons.append(
                BaseButton(
                    self.canvas,
                    img,
                    active,
                    img,          # lock 未使用
                    attention,
                    area,
                    cmd,
                    self.app.hover_time
                )
            )

        self.check_cursor()

    def check_cursor(self):
        # 画面が閉じられた後の安全策
        if not self.winfo_exists():
            return

        x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        y = self.master.winfo_pointery() - self.master.winfo_rooty()

        for button in self.buttons:
            active_cmd = button.update(x, y)

            # === 1. 回答ボタン('GOOD', 'SOSO', 'BAD')が確定した場合 ===
            if active_cmd in ('GOOD', 'SOSO', 'BAD'):
                # ★ここが重要: on_answer()を呼ばず、変数に保存するだけにする
                self.selected_cmd = active_cmd
                
                # 選び直し対応: 今選んだボタン以外をノーマル（未選択）に戻す
                for other_btn in self.buttons:
                    if other_btn != button and other_btn.cmd in ('GOOD', 'SOSO', 'BAD'):
                        other_btn.set_nomal()
            
            # === 2. NEXTボタンが確定した場合 ===
            elif active_cmd == 'NEXT':
                # 回答が選択されている場合のみ、ここで初めて遷移する
                if self.selected_cmd is not None:
                    self.on_answer(self.selected_cmd)
                    return # 画面遷移するのでループを抜ける
                else:
                    # まだ選んでいない場合はNEXTボタンを無効表示に戻す
                    button.set_nomal()

            # === 3. 選択状態の維持（見た目の処理） ===
            # カーソルが外れても、選択中の回答ボタンはずっと光らせておく
            if self.selected_cmd == button.cmd:
                button.set_active()

        self.master.after(20, self.check_cursor)

    def on_answer(self, answer):
        # 回答保存
        self.app.answers.append(answer)
        self.app.question_index += 1

        # 次へ
        if self.app.question_index >= len(self.app.questions):
            self.app.end_time = time.time()
            self.app.show_frame(FrameName.RESULT)
        else:
            next_frame = FrameName.QUESTION
            self.app.show_frame(next_frame)
class mainApp:
    def __init__(self):
        # 質問リスト
        """
        self.questions = [
            "とりくみがある日の朝の気分はどうでしたか？",
            "とりくみがおわった後の気分はどうでしたか？",
            "とりくみはつかれますか？",
            "おもったとおりに操縦できましたか？",
            "来年度もこのとりくみをしたいですか？",
        ]
        """
        self.questions = [
            "今、つかれていますか？",
            "今日はたのしくできましたか？",
            "おもったとおりに操縦できましたか？",
            "コースはむずかしかったですか？",
            "またやりたいですか？",
        ]
        #現在の質問番号
        self.question_index = 0
        self.answers = []  # ('GOOD' / 'SOSO' / 'BAD')

        #全体で共有するデータを定義
        self.root = tk.Tk()
        self.root.title('eye controll game')
        self.root.state("zoomed")
        self.current_frame = None#現在表示中のフレーム
        self.start_time = time.time()
        self.end_time = None
        self.hover_time = 0.5#滞留時間
        self.button_size_ratio = BUTTON_SIZE_RATIO
        self.show_frame(FrameName.READY)

    def show_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.destroy()
        if frame_name == FrameName.READY:
            self.current_frame = ReadyFrame(self.root, self)
        elif frame_name == FrameName.QUESTION:
            self.current_frame = QuestionFrame(self.root, self)
        elif frame_name == FrameName.RESULT:
            self.current_frame = ResultFrame(self.root, self)
        elif frame_name == FrameName.SETTING:
            self.current_frame = SettingFrame(self.root, self)
        elif frame_name == FrameName.ANSWER:
            self.current_frame = AnswerFrame(self.root, self)
    def run(self):
        self.root.mainloop()

def main():
    app = mainApp()
    app.run()

if __name__ == '__main__':
    main()