import tkinter as tk
from tkinter import ttk, messagebox


class UserView:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        """创建界面组件"""
        tk.Label(self.parent, text="👥 用户管理", font=("微软雅黑", 18, "bold"),
                 bg="white").pack(pady=(10, 15))

        control_frame = tk.Frame(self.parent, bg="white")
        control_frame.pack(pady=5, padx=20, fill='x')
        tk.Button(control_frame, text="🔄 刷新", command=self.load_users).pack(side='left', padx=5)
        self.count_label = tk.Label(control_frame, text="共 0 位用户", font=("微软雅黑", 10), bg="white")
        self.count_label.pack(side='right', padx=10)

        tree_frame = tk.Frame(self.parent, bg="white")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('用户ID', '用户名', '学习积分', '注册时间')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        col_widths = [80, 150, 100, 150]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='w')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def load_users(self):
        """加载所有用户"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        users = self.db.get_all_users()
        self.count_label.config(text=f"共 {len(users)} 位用户")

        for user in users:
            self.tree.insert('', 'end', values=(
                user['id'],
                user['username'],
                user['learning_score'],
                user['created_at'][:10] if user['created_at'] else ''
            ))