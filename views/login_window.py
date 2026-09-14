import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from utils.admin_config import is_admin, get_admin_user, ADMIN_USERNAME


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("红色文化学习打卡系统 - 登录")
        self.root.geometry("420x520")
        self.root.resizable(False, False)

        self.db = DatabaseManager()
        self.on_login_success = on_login_success

        self.setup_ui()

    def setup_ui(self):
        """设置界面：顶部标题 + 两个登录页签"""
        # 顶部标题
        header = tk.Frame(self.root, bg="#8B0000", height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="红色文化学习打卡系统",
                 font=("微软雅黑", 18, "bold"), fg="white", bg="#8B0000").pack(expand=True)

        # 页签：普通用户 / 管理员
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("微软雅黑", 11), padding=[20, 8])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.user_tab = tk.Frame(self.notebook, bg="white")
        self.admin_tab = tk.Frame(self.notebook, bg="#FFF5F5")

        self.notebook.add(self.user_tab, text="👤 普通用户登录")
        self.notebook.add(self.admin_tab, text="🔑 管理员登录")

        self.build_user_tab()
        self.build_admin_tab()

    # ================= 普通用户页签 =================
    def build_user_tab(self):
        """构建普通用户登录页签"""
        frame = tk.Frame(self.user_tab, bg="white")
        frame.pack(expand=True, fill='both', padx=40, pady=30)

        tk.Label(frame, text="用户登录", font=("微软雅黑", 14, "bold"),
                 fg="#333", bg="white").pack(pady=(0, 25))

        tk.Label(frame, text="用户名", font=("微软雅黑", 10), bg="white").pack(anchor='w')
        self.username_entry = tk.Entry(frame, font=("微软雅黑", 11), width=30)
        self.username_entry.pack(pady=(5, 15), fill='x')

        tk.Label(frame, text="密码", font=("微软雅黑", 10), bg="white").pack(anchor='w')
        self.password_entry = tk.Entry(frame, show="●", font=("微软雅黑", 11), width=30)
        self.password_entry.pack(pady=(5, 25), fill='x')

        tk.Button(frame, text="登 录", font=("微软雅黑", 11, "bold"),
                  bg="#2E7D32", fg="white", width=20, height=1,
                  command=self.user_login).pack(pady=10)

        tk.Label(frame, text="还没有账号？", font=("微软雅黑", 9), fg="#666",
                 bg="white").pack(pady=(25, 5))
        register_link = tk.Label(frame, text="立即注册", font=("微软雅黑", 10, "underline"),
                                 fg="#1565C0", bg="white", cursor="hand2")
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.show_register_dialog())

        # 回车登录
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus_set())
        self.password_entry.bind('<Return>', lambda e: self.user_login())

    def user_login(self):
        """普通用户登录验证（查数据库）"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码！")
            return

        # 引导：管理员账号请到管理员页签
        if username == ADMIN_USERNAME:
            messagebox.showinfo("提示", "admin 是内置管理员账号，请切换到「管理员登录」页签登录！")
            self.notebook.select(self.admin_tab)
            return

        # 验证普通用户（加盐哈希）
        user = self.db.verify_user_password(username, password)
        if user:
            user = dict(user)
            user['role'] = 'user'
            messagebox.showinfo("成功", f"登录成功！欢迎 {username}")
            self.on_login_success(user)
        else:
            messagebox.showerror("错误", "用户名或密码错误！\n（若尚未注册，请先点击「立即注册」）")

    # ================= 管理员页签 =================
    def build_admin_tab(self):
        """构建管理员登录页签（红色主题，独立入口）"""
        frame = tk.Frame(self.admin_tab, bg="#FFF5F5")
        frame.pack(expand=True, fill='both', padx=40, pady=30)

        tk.Label(frame, text="🔑 管理员登录", font=("微软雅黑", 14, "bold"),
                 fg="#8B0000", bg="#FFF5F5").pack(pady=(0, 10))
        tk.Label(frame, text="管理员为系统内置账号，不存于数据库",
                 font=("微软雅黑", 9), fg="#999", bg="#FFF5F5").pack(pady=(0, 20))

        tk.Label(frame, text="管理员账号", font=("微软雅黑", 10), bg="#FFF5F5").pack(anchor='w')
        self.admin_user_entry = tk.Entry(frame, font=("微软雅黑", 11), width=30)
        self.admin_user_entry.pack(pady=(5, 15), fill='x')

        tk.Label(frame, text="管理员密码", font=("微软雅黑", 10), bg="#FFF5F5").pack(anchor='w')
        self.admin_pass_entry = tk.Entry(frame, show="●", font=("微软雅黑", 11), width=30)
        self.admin_pass_entry.pack(pady=(5, 25), fill='x')

        tk.Button(frame, text="管理员登录", font=("微软雅黑", 11, "bold"),
                  bg="#8B0000", fg="white", width=20, height=1,
                  command=self.admin_login).pack(pady=10)

        tk.Label(frame, text=f"内置管理员账号：{ADMIN_USERNAME}（密码见 utils/admin_config.py）",
                 font=("微软雅黑", 9), fg="#8B0000", bg="#FFF5F5").pack(pady=(25, 5))

        # 回车登录
        self.admin_user_entry.bind('<Return>', lambda e: self.admin_pass_entry.focus_set())
        self.admin_pass_entry.bind('<Return>', lambda e: self.admin_login())

    def admin_login(self):
        """管理员登录验证（只校验内置配置，与数据库无关）"""
        username = self.admin_user_entry.get().strip()
        password = self.admin_pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("错误", "请输入管理员账号和密码！")
            return

        # 与数据库完全无关，直接校验内置配置
        if is_admin(username, password):
            messagebox.showinfo("成功", "管理员登录成功！")
            self.on_login_success(get_admin_user())
        else:
            messagebox.showerror(
                "登录失败",
                f"管理员账号或密码错误！\n内置管理员账号为：{ADMIN_USERNAME}\n"
                f"（密码配置于 utils/admin_config.py）"
            )

    # ================= 注册 =================
    def show_register_dialog(self):
        """注册对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("用户注册")
        dialog.geometry("400x360")
        dialog.resizable(False, False)
        dialog.grab_set()  # 模态

        tk.Label(dialog, text="用户注册", font=("微软雅黑", 16, "bold"),
                 fg="#8B0000").pack(pady=(15, 10))

        body = tk.Frame(dialog)
        body.pack(padx=30, fill='x')

        tk.Label(body, text="用户名（至少3个字符）", font=("微软雅黑", 10)).pack(anchor='w')
        reg_username = tk.Entry(body, font=("微软雅黑", 11), width=30)
        reg_username.pack(pady=(5, 15), fill='x')

        tk.Label(body, text="密码（至少6位）", font=("微软雅黑", 10)).pack(anchor='w')
        reg_password = tk.Entry(body, show="●", font=("微软雅黑", 11), width=30)
        reg_password.pack(pady=(5, 15), fill='x')

        tk.Label(body, text="确认密码", font=("微软雅黑", 10)).pack(anchor='w')
        reg_confirm = tk.Entry(body, show="●", font=("微软雅黑", 11), width=30)
        reg_confirm.pack(pady=(5, 20), fill='x')

        def register():
            username = reg_username.get().strip()
            password = reg_password.get().strip()
            confirm = reg_confirm.get().strip()

            if not username or not password:
                messagebox.showerror("错误", "用户名和密码不能为空！", parent=dialog)
                return

            if len(username) < 3:
                messagebox.showerror("错误", "用户名至少3个字符！", parent=dialog)
                return

            if username == ADMIN_USERNAME:
                messagebox.showerror("错误", "该用户名为系统保留（管理员），请更换！", parent=dialog)
                return

            if len(password) < 6:
                messagebox.showerror("错误", "密码至少6个字符！", parent=dialog)
                return

            if password != confirm:
                messagebox.showerror("错误", "两次输入的密码不一致！", parent=dialog)
                return

            if self.db.get_user_by_username(username):
                messagebox.showerror("错误", "用户名已存在！", parent=dialog)
                return

            try:
                self.db.create_user(username, password)
                messagebox.showinfo("成功", "注册成功！请使用新账号登录", parent=dialog)
                dialog.destroy()
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, username)
                self.password_entry.focus_set()
            except Exception as e:
                messagebox.showerror("错误", f"注册失败：{str(e)}", parent=dialog)

        tk.Button(dialog, text="注 册", font=("微软雅黑", 11, "bold"),
                  bg="#8B0000", fg="white", width=18,
                  command=register).pack(pady=5)
        dialog.bind('<Return>', lambda e: register())
