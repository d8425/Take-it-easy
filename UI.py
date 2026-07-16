import flet as ft
import seleted_ROI
import LLM
from datetime import datetime
from PIL import ImageGrab

api_key = r""

def main(page: ft.Page):
    # ===== 最简单方案：保留窗口框架 =====
    page.title = "Take it easy"
    page.window.width = 600
    page.window.height = 650  # 调高一点容纳日志区域
    page.window.center()
    page.bgcolor = ft.Colors.GREY_50

    location = None  # 存储结果

    # ===== 日志相关 =====
    log_list = ft.ListView(
        spacing=3,
        padding=5,
        auto_scroll=True,
        height=250,  # 固定高度
    )

    def add_log(message, level="INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": ft.Colors.BLUE,
            "SUCCESS": ft.Colors.GREEN,
            "ERROR": ft.Colors.RED,
            "WARNING": ft.Colors.ORANGE,
        }
        log_list.controls.append(
            ft.Row(
                [
                    ft.Text(f"[{timestamp}]", size=11, color=ft.Colors.GREY_400, width=65),
                    ft.Text(message, size=12, color=colors.get(level, ft.Colors.BLACK),selectable=True),
                ],
                spacing=5,
            )
        )
        page.update()

    # ===== 功能函数 =====
    def _get_roi(e):
        global location
        add_log("🔄 正在选取回答区域...", "INFO")
        try:
            location = seleted_ROI.HollowResizeBox()
            add_log(f"✅ 图像区域已确认: {location}", "SUCCESS")
            print(f"图像区域已确认: {location}")
            text = LLM.qwen_vlm_ocr_extract(r"./screenshot.png", api_key)
            add_log(f"识别文本:\n {text}" )
        except Exception as ex:
            add_log(f"❌ 选取失败: {str(ex)}", "ERROR")

    def _get_standard(e):
        global text
        add_log("📋 正在选取标答区域...", "INFO")
        seleted_ROI.HollowResizeBox()
        print(f"标答内容已确认")
        text = LLM.qwen_vlm_ocr_extract(r"./screenshot.png", api_key)
        add_log(f"标答文本:\n {text}")
        # TODO: 实现标答选取逻辑
        add_log("✅ 标答已选取", "SUCCESS")

    def _get_answer_roi(e):
        global location_manual,text_manual
        location_manual = seleted_ROI.HollowResizeBox()
        add_log("🧮 回答提取完成...", "INFO")

    def _cal_result(e):
        add_log("🧮 计算分数中...", "INFO")
        screenshot = ImageGrab.grab(bbox=location_manual)
        filename = "screenshot_manual.png"
        screenshot.save(filename)
        text_manual = LLM.qwen_vlm_ocr_extract(r"./screenshot_manual.png", api_key)
        result = LLM.qwen_text_judge(text_manual, text, 6, api_key)
        add_log(f"🧮 打分: {result}", "INFO")

    # def _open_settings(e):
    #     add_log("⚙️ 打开设置", "INFO")
    #
    # def _open_folder(e):
    #     add_log("📁 打开文件", "INFO")
    #
    # def _open_cloud(e):
    #     add_log("☁️ 打开云盘", "INFO")

    # ===== 清空日志 =====
    def _clear_logs(e):
        log_list.controls.clear()
        add_log("🗑️ 日志已清空", "INFO")

    class ToolCard(ft.Container):
        def __init__(self, icon_name, label, on_click):
            super().__init__(
                content=ft.Column(
                    [
                        ft.Icon(name=icon_name, size=30, color=ft.Colors.BLUE),
                        ft.Text(label, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                width=80,
                height=80,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                alignment=ft.alignment.center,
                on_click=on_click,
                ink=True,
            )

    tool_box = ft.Container(
        content=ft.Column(
            [
                # ===== 标题栏 =====
                ft.Row(
                    [
                        ft.Text("✨ Take it easy", size=24, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon="MINIMIZE",
                                    icon_size=20,
                                    on_click=lambda e: page.window.minimize(),
                                ),
                                ft.IconButton(
                                    icon="CLOSE",
                                    icon_size=20,
                                    on_click=lambda e: page.window.close(),
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                # ===== 第一行：1个功能（居中） =====
                ft.Row(
                    [
                        ToolCard("PHOTO", "提取文字", _get_roi),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=15,
                ),

                # ===== 第二行：5个功能 =====
                ft.Row(
                    [
                        ToolCard("PHOTO", "选取标答", _get_standard),
                        ToolCard("VIDEO_FILE", "框选回答区域(勿移答区)", _get_answer_roi),
                        ToolCard("SETTINGS", "计算分数", _cal_result),
                        # ToolCard("FOLDER", "文件", _open_folder),
                        # ToolCard("CLOUD", "云盘", _open_cloud),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=15,
                    wrap=True,
                ),

                # ===== 日志区域 =====
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("📋 日志", size=14, weight=ft.FontWeight.BOLD),
                                    ft.IconButton(
                                        icon="DELETE_OUTLINE",
                                        icon_size=18,
                                        on_click=_clear_logs,
                                        tooltip="清空日志",
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(
                                content=log_list,
                                height=200,
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=8,
                                padding=5,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ],
            spacing=15,
        ),
        padding=30,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        shadow=ft.BoxShadow(
            blur_radius=15,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK)
        ),
        width=600,
    )

    page.add(tool_box)

    # ===== 启动日志 =====
    add_log("🚀 Take it easy 已启动", "SUCCESS")
    add_log("💡 点击功能按钮开始使用", "INFO")
    page.update()


if __name__ == "__main__":
    ft.app(target=main)