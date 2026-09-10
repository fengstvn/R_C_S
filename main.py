import tkinter as tk
from views.login_window import LoginWindow


def main():
    root = tk.Tk()

    def on_login_success(user):
        """登录成功后的回调函数"""
        from views.main_window import MainWindow
        # 清除当前窗口内容
        for widget in root.winfo_children():
            widget.destroy()
        # 显示主窗口
        MainWindow(root, user)

    # 显示登录窗口
    LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()