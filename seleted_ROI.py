import tkinter as tk
from PIL import ImageGrab
import time


class HollowResizeBox:
    def __init__(self):
        self.win = tk.Tk()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.trans_color = "#000001"
        self.win.attributes("-transparentcolor", self.trans_color)

        self.box_w, self.box_h = 400, 250
        self.pos_x, self.pos_y = 300, 200
        self.win.geometry(f"{self.box_w}x{self.box_h}+{self.pos_x}+{self.pos_y}")
        self.win.configure(bg=self.trans_color)

        self.canvas = tk.Canvas(self.win, bg=self.trans_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.rect = self.canvas.create_rectangle(
            2, 2, self.box_w - 2, self.box_h - 2,
            outline="#00ff00", width=3, fill=""
        )
        self.canvas.create_text(
            self.box_w // 2, self.box_h // 2,
            text="拖动框移动｜右下角拖动缩放\nEnter 截图输出",
            fill="#00ff00", font=("微软雅黑", 10), tags="text_tag"
        )

        self.drag_x = None
        self.drag_y = None
        self.is_resizing = False
        self.resize_margin = 10

        # ===== 新增：存储坐标 =====
        self.region = None

        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)

        self.win.bind("<Return>", self.screenshot_and_exit)
        self.win.mainloop()

    def get_cursor_area(self, event):
        x, y = event.x, event.y
        w = self.win.winfo_width()
        h = self.win.winfo_height()
        if w - self.resize_margin <= x <= w and h - self.resize_margin <= y <= h:
            return "resize"
        return "move"

    def mouse_down(self, event):
        area = self.get_cursor_area(event)
        if area == "resize":
            self.is_resizing = True
        else:
            self.is_resizing = False
            self.drag_x = event.x
            self.drag_y = event.y

    def mouse_move(self, event):
        if self.is_resizing:
            new_w = max(100, event.x)
            new_h = max(80, event.y)
            self.box_w, self.box_h = new_w, new_h
            self.win.geometry(f"{new_w}x{new_h}")
            self.canvas.coords(self.rect, 2, 2, new_w - 2, new_h - 2)
            self.canvas.delete("text_tag")
            self.canvas.create_text(
                new_w // 2, new_h // 2,
                text="拖动框移动｜右下角拖动缩放\nEnter 截图输出",
                fill="#00ff00", font=("微软雅黑", 10), tags="text_tag"
            )
        else:
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            x = self.win.winfo_x() + dx
            y = self.win.winfo_y() + dy
            self.win.geometry(f"+{x}+{y}")

    def mouse_up(self, event):
        self.drag_x = None
        self.drag_y = None
        self.is_resizing = False

    def screenshot_and_exit(self, event):
        """截图并保存"""
        # 获取选区坐标
        x1 = self.win.winfo_x()
        y1 = self.win.winfo_y()
        x2 = x1 + self.win.winfo_width()
        y2 = y1 + self.win.winfo_height()

        # ===== 保存到实例属性 =====
        self.region = (x1, y1, x2, y2)

        print("=== 选区坐标 ===")
        print(f"bbox = {self.region}")

        # 隐藏窗口
        self.win.withdraw()
        self.win.update()
        time.sleep(0.1)

        # 截图
        try:
            screenshot = ImageGrab.grab(bbox=self.region)
            filename = "screenshot.png"
            screenshot.save(filename)
            print(f"✅ 截图已保存: {filename}")
        except Exception as e:
            print(f"❌ 截图失败: {e}")

        # 关闭窗口
        self.win.destroy()

    # ===== 新增：获取坐标方法 =====
    def get_region(self):
        return self.region

    # ===== 支持解包 =====
    def __iter__(self):
        return iter(self.region) if self.region else iter((0, 0, 0, 0))


if __name__ == "__main__":
    roi = HollowResizeBox()
    print(f"外部获取坐标: {roi.get_region()}")
    # 或者直接访问属性
    # print(f"外部获取坐标: {roi.region}")