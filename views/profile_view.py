import tkinter as tk
from tkinter import messagebox, ttk


class ProfileView:
    def __init__(self, parent, db, user, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.user = user
        self.refresh_callback = refresh_callback
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        tk.Label(self.parent, text="👤 个人信息", font=("微软雅黑", 18, "bold"),
                 bg="white").pack(pady=(10, 20))

        # 信息卡片
        card = tk.Frame(self.parent, bg="#F5F5F5", relief='ridge', bd=2)
        card.pack(pady=10, padx=40, fill='x')

        info = f"""
        用户名: {self.user['username']}
        用户ID: {self.user['id']}
        学习积分: {self.user['learning_score']}
        角色: {'管理员' if self.user.get('role') == 'admin' else '普通用户'}
        注册时间: {self.user.get('created_at', '未知')}
        """

        tk.Label(card, text=info, font=("微软雅黑", 12), bg="#F5F5F5",
                 justify='left').pack(pady=20, padx=30, anchor='w')

        # 修改按钮
        btn_frame = tk.Frame(self.parent, bg="white")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="修改用户名", command=self.change_username,
                  font=("微软雅黑", 10), width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="修改密码", command=self.change_password,
                  font=("微软雅黑", 10), width=15).pack(side='left', padx=10)

        # 统计信息
        stats_frame = tk.Frame(self.parent, bg="white")
        stats_frame.pack(pady=20, padx=40, fill='x')

        records = self.db.get_records_by_user(self.user['id'])
        total_records = len(records)

        stats_text = f"📊 统计信息：\n总打卡次数: {total_records} 次"
        tk.Label(stats_frame, text=stats_text, font=("微软雅黑", 11), bg="white",
                 justify='left').pack(anchor='w')

    def change_username(self):
        """修改用户名"""
        if self.user.get('role') == 'admin':
            messagebox.showinfo("提示", "管理员用户名不可修改！")
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("修改用户名")
        dialog.geometry("350x200")

        tk.Label(dialog, text="修改用户名", font=("微软雅黑", 14, "bold")).pack(pady=15)

        tk.Label(dialog, text="新用户名:", font=("微软雅黑", 10)).pack()
        new_name_entry = tk.Entry(dialog, width=30, font=("微软雅黑", 10))
        new_name_entry.pack(pady=5)
        new_name_entry.insert(0, self.user['username'])

        def save():
            new_name = new_name_entry.get().strip()
            if not new_name or len(new_name) < 3:
                messagebox.showerror("错误", "用户名至少3个字符！")
                return

            existing = self.db.get_user_by_username(new_name)
            if existing and existing['id'] != self.user['id']:
                messagebox.showerror("错误", "用户名已被占用！")
                return

            try:
                self.db.update_username(self.user['id'], new_name)
                self.user['username'] = new_name
                messagebox.showinfo("成功", "用户名修改成功！")
                dialog.destroy()
                if self.refresh_callback:
                    self.refresh_callback()
                self.create_widgets()
            except Exception as e:
                messagebox.showerror("错误", f"修改失败：{str(e)}")

        tk.Button(dialog, text="保存", command=save, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 10)).pack(pady=15)

    def change_password(self):
        """修改密码"""
        if self.user.get('role') == 'admin':
            messagebox.showinfo("提示", "管理员密码不可在此修改！")
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("修改密码")
        dialog.geometry("350x280")

        tk.Label(dialog, text="修改密码", font=("微软雅黑", 14, "bold")).pack(pady=15)

        tk.Label(dialog, text="当前密码:", font=("微软雅黑", 10)).pack()
        old_pass = tk.Entry(dialog, show="●", width=30, font=("微软雅黑", 10))
        old_pass.pack(pady=5)

        tk.Label(dialog, text="新密码:", font=("微软雅黑", 10)).pack()
        new_pass = tk.Entry(dialog, show="●", width=30, font=("微软雅黑", 10))
        new_pass.pack(pady=5)

        tk.Label(dialog, text="确认新密码:", font=("微软雅黑", 10)).pack()
        confirm_pass = tk.Entry(dialog, show="●", width=30, font=("微软雅黑", 10))
        confirm_pass.pack(pady=5)

        def save():
            old = old_pass.get().strip()
            new = new_pass.get().strip()
            confirm = confirm_pass.get().strip()

            # 验证当前密码
            if not self.db.verify_user_password(self.user['username'], old):
                messagebox.showerror("错误", "当前密码错误！")
                return

            if len(new) < 6:
                messagebox.showerror("错误", "新密码至少6个字符！")
                return

            if new != confirm:
                messagebox.showerror("错误", "两次输入的新密码不一致！")
                return

            try:
                self.db.update_user_password(self.user['id'], new)
                messagebox.showinfo("成功", "密码修改成功！")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"修改失败：{str(e)}")

        tk.Button(dialog, text="保存", command=save, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 10)).pack(pady=15)