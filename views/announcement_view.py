import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class AnnouncementView:
    def __init__(self, parent, db, is_admin):
        self.parent = parent
        self.db = db
        self.is_admin = is_admin

        self.create_widgets()
        self.load_announcements()

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        tk.Label(self.parent, text="📢 公告管理", font=("微软雅黑", 18, "bold"),
                 bg="white").pack(pady=(10, 15))

        # 搜索框
        search_frame = tk.Frame(self.parent, bg="white")
        search_frame.pack(pady=5, padx=20, fill='x')

        tk.Label(search_frame, text="搜索:", bg="white", font=("微软雅黑", 10)).pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("微软雅黑", 10))
        search_entry.pack(side='left', padx=5)

        search_btn = tk.Button(search_frame, text="按标题搜索", command=self.search_by_title)
        search_btn.pack(side='left', padx=5)

        search_id_btn = tk.Button(search_frame, text="按编号搜索", command=self.search_by_id)
        search_id_btn.pack(side='left', padx=5)

        show_all_btn = tk.Button(search_frame, text="显示全部", command=self.load_announcements)
        show_all_btn.pack(side='left', padx=5)

        if self.is_admin:
            add_btn = tk.Button(search_frame, text="➕ 发布公告", bg="#4CAF50", fg="white",
                                command=self.show_add_dialog)
            add_btn.pack(side='right', padx=5)

        # 公告列表（Treeview）
        tree_frame = tk.Frame(self.parent, bg="white")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('编号', '标题', '内容', '发布日期', '备注')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # 设置列宽
        col_widths = [60, 150, 350, 150, 100]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='w')

        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 绑定双击事件查看详情
        self.tree.bind('<Double-Button-1>', self.view_announcement_detail)

        # 操作按钮（管理员）
        if self.is_admin:
            btn_frame = tk.Frame(self.parent, bg="white")
            btn_frame.pack(pady=10)

            tk.Button(btn_frame, text="编辑", command=self.edit_announcement).pack(side='left', padx=5)
            tk.Button(btn_frame, text="删除", command=self.delete_announcement,
                      bg="#FF6B6B", fg="white").pack(side='left', padx=5)

    def load_announcements(self):
        """加载所有公告"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        announcements = self.db.get_all_announcements()
        for ann in announcements:
            self.tree.insert('', 'end', values=(
                ann['announcement_id'],
                ann['title'],
                ann['content'][:50] + ('...' if len(ann['content']) > 50 else ''),
                ann['created_at'][:10] if ann['created_at'] else '',
                ann['remark'] or ''
            ))

    def search_by_title(self):
        """按标题搜索"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showinfo("提示", "请输入搜索关键词！")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        results = self.db.search_announcements_by_title(keyword)
        for ann in results:
            self.tree.insert('', 'end', values=(
                ann['announcement_id'],
                ann['title'],
                ann['content'][:50] + ('...' if len(ann['content']) > 50 else ''),
                ann['created_at'][:10] if ann['created_at'] else '',
                ann['remark'] or ''
            ))

    def search_by_id(self):
        """按编号搜索"""
        ann_id = self.search_var.get().strip()
        if not ann_id.isdigit():
            messagebox.showerror("错误", "请输入有效的公告编号！")
            return

        ann = self.db.get_announcement_by_id(int(ann_id))
        if not ann:
            messagebox.showinfo("提示", "未找到该公告！")
            return

        self.view_announcement_detail(None, ann_id=int(ann_id))

    def view_announcement_detail(self, event, ann_id=None):
        """查看公告详情"""
        if ann_id is None:
            selected = self.tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请先选择一条公告！")
                return
            values = self.tree.item(selected[0])['values']
            ann_id = values[0]

        ann = self.db.get_announcement_by_id(int(ann_id))
        if not ann:
            return

        # 弹出详情窗口
        detail_win = tk.Toplevel(self.parent)
        detail_win.title(f"公告详情 - {ann['title']}")
        detail_win.geometry("500x400")
        detail_win.resizable(False, False)

        tk.Label(detail_win, text=f"📢 {ann['title']}", font=("微软雅黑", 16, "bold"),
                 fg="#8B0000").pack(pady=10)

        info = f"""
        编号: {ann['announcement_id']}
        发布日期: {ann['created_at']}
        备注: {ann['remark'] or '无'}
        """
        tk.Label(detail_win, text=info, font=("微软雅黑", 10), justify='left').pack(pady=5, padx=20, anchor='w')

        tk.Label(detail_win, text="公告内容:", font=("微软雅黑", 11, "bold")).pack(anchor='w', padx=20)
        text_area = scrolledtext.ScrolledText(detail_win, height=10, font=("微软雅黑", 10))
        text_area.pack(pady=5, padx=20, fill='both', expand=True)
        text_area.insert('1.0', ann['content'])
        text_area.config(state='disabled')

    def show_add_dialog(self):
        """显示添加公告对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("发布公告")
        dialog.geometry("450x400")

        tk.Label(dialog, text="发布新公告", font=("微软雅黑", 14, "bold")).pack(pady=10)

        # 标题
        tk.Label(dialog, text="公告标题:", font=("微软雅黑", 10)).pack(anchor='w', padx=20)
        title_entry = tk.Entry(dialog, width=50, font=("微软雅黑", 10))
        title_entry.pack(pady=5, padx=20, fill='x')

        # 内容
        tk.Label(dialog, text="公告内容:", font=("微软雅黑", 10)).pack(anchor='w', padx=20, pady=(10, 0))
        content_text = scrolledtext.ScrolledText(dialog, height=8, font=("微软雅黑", 10))
        content_text.pack(pady=5, padx=20, fill='x')

        # 备注
        tk.Label(dialog, text="备注:", font=("微软雅黑", 10)).pack(anchor='w', padx=20, pady=(10, 0))
        remark_entry = tk.Entry(dialog, width=50, font=("微软雅黑", 10))
        remark_entry.pack(pady=5, padx=20, fill='x')

        def save():
            title = title_entry.get().strip()
            content = content_text.get('1.0', 'end-1c').strip()
            remark = remark_entry.get().strip()

            if not title or not content:
                messagebox.showerror("错误", "标题和内容不能为空！")
                return

            try:
                self.db.create_announcement(title, content, remark)
                messagebox.showinfo("成功", "公告发布成功！")
                dialog.destroy()
                self.load_announcements()
            except Exception as e:
                messagebox.showerror("错误", f"发布失败：{str(e)}")

        tk.Button(dialog, text="发布", command=save, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 10), width=15).pack(pady=15)

    def edit_announcement(self):
        """编辑公告"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要编辑的公告！")
            return

        values = self.tree.item(selected[0])['values']
        ann_id = values[0]
        ann = self.db.get_announcement_by_id(ann_id)

        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑公告")
        dialog.geometry("450x400")

        tk.Label(dialog, text="编辑公告", font=("微软雅黑", 14, "bold")).pack(pady=10)

        tk.Label(dialog, text="公告标题:", font=("微软雅黑", 10)).pack(anchor='w', padx=20)
        title_entry = tk.Entry(dialog, width=50, font=("微软雅黑", 10))
        title_entry.insert(0, ann['title'])
        title_entry.pack(pady=5, padx=20, fill='x')

        tk.Label(dialog, text="公告内容:", font=("微软雅黑", 10)).pack(anchor='w', padx=20, pady=(10, 0))
        content_text = scrolledtext.ScrolledText(dialog, height=8, font=("微软雅黑", 10))
        content_text.insert('1.0', ann['content'])
        content_text.pack(pady=5, padx=20, fill='x')

        tk.Label(dialog, text="备注:", font=("微软雅黑", 10)).pack(anchor='w', padx=20, pady=(10, 0))
        remark_entry = tk.Entry(dialog, width=50, font=("微软雅黑", 10))
        remark_entry.insert(0, ann['remark'] or '')
        remark_entry.pack(pady=5, padx=20, fill='x')

        def save():
            title = title_entry.get().strip()
            content = content_text.get('1.0', 'end-1c').strip()
            remark = remark_entry.get().strip()

            if not title or not content:
                messagebox.showerror("错误", "标题和内容不能为空！")
                return

            try:
                self.db.update_announcement(ann_id, title=title, content=content, remark=remark)
                messagebox.showinfo("成功", "公告更新成功！")
                dialog.destroy()
                self.load_announcements()
            except Exception as e:
                messagebox.showerror("错误", f"更新失败：{str(e)}")

        tk.Button(dialog, text="保存", command=save, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 10), width=15).pack(pady=15)

    def delete_announcement(self):
        """删除公告"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的公告！")
            return

        if not messagebox.askyesno("确认", "确定要删除该公告吗？\n删除后不可恢复！"):
            return

        values = self.tree.item(selected[0])['values']
        ann_id = values[0]

        try:
            self.db.delete_announcement(ann_id)
            messagebox.showinfo("成功", "公告删除成功！")
            self.load_announcements()
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")