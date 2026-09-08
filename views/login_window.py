import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("红色文化学习打卡系统 - 登录")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        self.db = DatabaseManager()
        self.on_login_success = on_login_success
        self.current_frame = None

        self.show_login()

    def clear_frame(self):
        """清空当前框架"""
        if self.current_frame:
            self.current_frame.destroy()

    def show_login(self):
        """显示登录界面"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # 标题
        tk.Label(self.current_frame, text="红色文化学习打卡",
                 font=("微软雅黑", 18, "bold"), fg="#8B0000").pack(pady=(0, 10))
        tk.Label(self.current_frame, text="登录系统",
                 font=("微软雅黑", 12), fg="#666").pack(pady=(0, 30))

        # 用户名
        tk.Label(self.current_frame, text="用户名", font=("微软雅黑", 10)).pack(anchor='w')
        self.username_entry = tk.Entry(self.current_frame, font=("微软雅黑", 11), width=30)
        self.username_entry.pack(pady=(5, 15), fill='x')

        # 密码
        tk.Label(self.current_frame, text="密码", font=("微软雅黑", 10)).pack(anchor='w')
        self.password_entry = tk.Entry(self.current_frame, show="●", font=("微软雅黑", 11), width=30)
        self.password_entry.pack(pady=(5, 20), fill='x')

        # 登录按钮
        login_btn = tk.Button(self.current_frame, text="登 录",
                              font=("微软雅黑", 11, "bold"), bg="#8B0000", fg="white",
                              width=20, height=1, command=self.login)
        login_btn.pack(pady=10)

        # 注册跳转
        tk.Label(self.current_frame, text="还没有账号？", font=("微软雅黑", 9), fg="#666").pack(pady=(20, 5))
        register_link = tk.Label(self.current_frame, text="立即注册",
                                 font=("微软雅黑", 9, "underline"), fg="#0066CC", cursor="hand2")
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.show_register())

        # 绑定回车键
        self.root.bind('<Return>', lambda e: self.login())

    def show_register(self):
        """显示注册界面"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(expand=True, fill='both', padx=40, pady=40)

        tk.Label(self.current_frame, text="用户注册",
                 font=("微软雅黑", 18, "bold"), fg="#8B0000").pack(pady=(0, 20))

        # 用户名
        tk.Label(self.current_frame, text="用户名", font=("微软雅黑", 10)).pack(anchor='w')
        self.reg_username = tk.Entry(self.current_frame, font=("微软雅黑", 11), width=30)
        self.reg_username.pack(pady=(5, 15), fill='x')

        # 密码
        tk.Label(self.current_frame, text="密码", font=("微软雅黑", 10)).pack(anchor='w')
        self.reg_password = tk.Entry(self.current_frame, show="●", font=("微软雅黑", 11), width=30)
        self.reg_password.pack(pady=(5, 15), fill='x')

        # 确认密码
        tk.Label(self.current_frame, text="确认密码", font=("微软雅黑", 10)).pack(anchor='w')
        self.reg_confirm = tk.Entry(self.current_frame, show="●", font=("微软雅黑", 11), width=30)
        self.reg_confirm.pack(pady=(5, 20), fill='x')

        # 注册按钮
        reg_btn = tk.Button(self.current_frame, text="注 册",
                            font=("微软雅黑", 11, "bold"), bg="#8B0000", fg="white",
                            width=20, height=1, command=self.register)
        reg_btn.pack(pady=10)

        # 返回登录
        back_link = tk.Label(self.current_frame, text="← 返回登录",
                             font=("微软雅黑", 9, "underline"), fg="#0066CC", cursor="hand2")
        back_link.pack(pady=(20, 0))
        back_link.bind("<Button-1>", lambda e: self.show_login())

    def login(self):
        """登录验证"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码！")
            return

        user = self.db.get_user_by_username(username)
        if not user or user['password'] != password:
            messagebox.showerror("错误", "用户名或密码错误！")
            return

        messagebox.showinfo("成功", f"登录成功！欢迎 {username}")
        self.on_login_success(user)

    def register(self):
        """注册新用户"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空！")
            return

        if len(username) < 3:
            messagebox.showerror("错误", "用户名至少3个字符！")
            return

        if len(password) < 6:
            messagebox.showerror("错误", "密码至少6个字符！")
            return

        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致！")
            return

        # 检查用户名是否已存在
        if self.db.get_user_by_username(username):
            messagebox.showerror("错误", "用户名已存在，请换一个！")
            return

        try:
            user_id = self.db.create_user(username, password)
            messagebox.showinfo("成功", "注册成功！请返回登录")
            self.show_login()
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
        except Exception as e:
            messagebox.showerror("错误", f"注册失败：{str(e)}")