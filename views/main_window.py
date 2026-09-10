import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager


class MainWindow:
    def __init__(self, root, user):
        self.root = root
        self.root.title(f"红色文化学习打卡系统 - {user['username']}")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.user = user
        self.db = DatabaseManager()
        self.current_view = None

        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        # 顶部信息栏
        top_frame = tk.Frame(self.root, bg="#8B0000", height=70)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)

        # 用户信息
        info_text = f"👤 {self.user['username']}  |  学习积分: {self.user['learning_score']}"
        if self.user.get('role') == 'admin':
            info_text += "  |  🔑 管理员"

        self.info_label = tk.Label(top_frame, text=info_text, font=("微软雅黑", 12),
                                   fg="white", bg="#8B0000")
        self.info_label.pack(side='left', padx=20, pady=20)

        # 退出按钮
        exit_btn = tk.Button(top_frame, text="退出登录", font=("微软雅黑", 10),
                             bg="#FF6B6B", fg="white", command=self.logout)
        exit_btn.pack(side='right', padx=20, pady=20)

        # 主体区域
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True)

        # 左侧导航
        nav_frame = tk.Frame(main_container, width=180, bg="#F5F5F5")
        nav_frame.pack(side='left', fill='y')
        nav_frame.pack_propagate(False)

        # 导航按钮
        nav_buttons = [
            ("📢 公告管理", self.show_notices),
            ("🏛️ 景点管理", self.show_places),
            ("⭐ 热门景点", self.show_hot_places),
            ("👤 个人信息", self.show_profile),
            ("📝 打卡记录", self.show_records),
        ]

        if self.user.get('role') == 'admin':
            nav_buttons.insert(2, ("👥 用户管理", self.show_users))

        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, font=("微软雅黑", 11),
                            bg="#F5F5F5", fg="#333", bd=0, anchor='w',
                            padx=20, pady=12, width=20, command=command)
            btn.pack(fill='x')
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E8E8E8"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#F5F5F5"))

        # 右侧内容区域
        self.content_frame = tk.Frame(main_container, bg="white")
        self.content_frame.pack(side='right', fill='both', expand=True)

        # 默认显示公告
        self.show_notices()

    def clear_content(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_notices(self):
        """显示公告管理"""
        self.clear_content()
        from views.notice_view import NoticeView
        NoticeView(self.content_frame, self.db, self.user.get('role') == 'admin')

    def show_places(self):
        """显示景点管理"""
        self.clear_content()
        from views.place_view import PlaceView
        PlaceView(self.content_frame, self.db, self.user.get('role') == 'admin')

    def show_hot_places(self):
        """显示热门景点"""
        self.clear_content()
        from views.place_view import HotPlaceView
        HotPlaceView(self.content_frame, self.db)

    def show_profile(self):
        """显示个人信息"""
        self.clear_content()
        from views.profile_view import ProfileView
        ProfileView(self.content_frame, self.db, self.user, self.update_user_info)

    def show_records(self):
        """显示打卡记录"""
        self.clear_content()
        from views.record_view import RecordView
        RecordView(self.content_frame, self.db, self.user['id'], self.update_user_info)

    def show_users(self):
        """显示用户管理（管理员）"""
        self.clear_content()
        from views.user_view import UserView
        UserView(self.content_frame, self.db)

    def update_user_info(self):
        """更新用户信息显示"""
        if self.user.get('role') == 'admin':
            # 管理员直接更新
            info_text = f"👤 {self.user['username']}  |  学习积分: {self.user['learning_score']}  |  🔑 管理员"
            self.info_label.config(text=info_text)
        else:
            # 重新获取用户信息
            updated_user = self.db.get_user_by_id(self.user['id'])
            if updated_user:
                self.user = dict(updated_user)
                self.user['role'] = 'user'
                info_text = f"👤 {self.user['username']}  |  学习积分: {self.user['learning_score']}"
                self.info_label.config(text=info_text)

    def logout(self):
        """退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.root.destroy()
            from views.login_window import LoginWindow
            new_root = tk.Tk()
            LoginWindow(new_root, self.on_login_success)
            new_root.mainloop()

    def on_login_success(self, user):
        """登录成功回调"""
        self.user = user
        self.update_user_info()