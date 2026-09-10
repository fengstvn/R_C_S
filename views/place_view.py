import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class PlaceView:
    def __init__(self, parent, db, is_admin):
        self.parent = parent
        self.db = db
        self.is_admin = is_admin
        self.create_widgets()
        self.load_places()

    def create_widgets(self):
        """创建界面组件"""
        tk.Label(self.parent, text="🏛️ 景点管理", font=("微软雅黑", 18, "bold"),
                 bg="white").pack(pady=(10, 15))

        # 搜索框
        search_frame = tk.Frame(self.parent, bg="white")
        search_frame.pack(pady=5, padx=20, fill='x')

        tk.Label(search_frame, text="搜索:", bg="white", font=("微软雅黑", 10)).pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("微软雅黑", 10))
        search_entry.pack(side='left', padx=5)

        tk.Button(search_frame, text="按名称搜索", command=self.search_by_name).pack(side='left', padx=5)
        tk.Button(search_frame, text="按编号搜索", command=self.search_by_id).pack(side='left', padx=5)
        tk.Button(search_frame, text="显示全部", command=self.load_places).pack(side='left', padx=5)

        if self.is_admin:
            tk.Button(search_frame, text="➕ 添加景点", bg="#4CAF50", fg="white",
                      command=self.show_add_dialog).pack(side='right', padx=5)

        # 景点列表
        tree_frame = tk.Frame(self.parent, bg="white")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('编号', '景点名', '地理位置', '描述', '打卡次数', '热门')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        col_widths = [60, 150, 150, 250, 80, 60]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='w')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<Double-Button-1>', self.view_place_detail)

        if self.is_admin:
            btn_frame = tk.Frame(self.parent, bg="white")
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="编辑", command=self.edit_place).pack(side='left', padx=5)
            tk.Button(btn_frame, text="删除", command=self.delete_place,
                      bg="#FF6B6B", fg="white").pack(side='left', padx=5)

    def load_places(self):
        """加载所有景点"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        places = self.db.get_all_places()
        for place in places:
            self.tree.insert('', 'end', values=(
                place['id'],
                place['name'],
                place['location'],
                place['description'][:30] + ('...' if len(place['description']) > 30 else ''),
                place['checkin_count'],
                '⭐' if place['is_hot'] else ''
            ))

    def search_by_name(self):
        """按名称搜索"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showinfo("提示", "请输入景点名称！")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        results = self.db.search_places_by_name(keyword)
        for place in results:
            self.tree.insert('', 'end', values=(
                place['id'],
                place['name'],
                place['location'],
                place['description'][:30] + ('...' if len(place['description']) > 30 else ''),
                place['checkin_count'],
                '⭐' if place['is_hot'] else ''
            ))

    def search_by_id(self):
        """按编号搜索"""
        place_id = self.search_var.get().strip()
        if not place_id.isdigit():
            messagebox.showerror("错误", "请输入有效的景点编号！")
            return

        place = self.db.get_place_by_id(int(place_id))
        if not place:
            messagebox.showinfo("提示", "未找到该景点！")
            return

        self.view_place_detail(None, place_id=int(place_id))

    def view_place_detail(self, event, place_id=None):
        """查看景点详情"""
        if place_id is None:
            selected = self.tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请先选择一个景点！")
                return
            values = self.tree.item(selected[0])['values']
            place_id = values[0]

        place = self.db.get_place_by_id(int(place_id))
        if not place:
            return

        detail_win = tk.Toplevel(self.parent)
        detail_win.title(f"景点详情 - {place['name']}")
        detail_win.geometry("500x400")

        tk.Label(detail_win, text=f"🏛️ {place['name']}", font=("微软雅黑", 16, "bold"),
                 fg="#8B0000").pack(pady=10)

        info = f"""
        编号: {place['id']}
        地理位置: {place['location']}
        红色历史: {place['description']}
        打卡次数: {place['checkin_count']}
        热门状态: {'⭐ 热门景点' if place['is_hot'] else '普通景点'}
        """
        tk.Label(detail_win, text=info, font=("微软雅黑", 11), justify='left').pack(pady=10, padx=20)

    def show_add_dialog(self):
        """显示添加景点对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加景点")
        dialog.geometry("400x450")

        tk.Label(dialog, text="添加新景点", font=("微软雅黑", 14, "bold")).pack(pady=10)

        fields = [
            ("景点名:", "name"),
            ("地理位置:", "location"),
            ("红色历史描述:", "description")
        ]

        entries = {}
        for label, key in fields:
            frame = tk.Frame(dialog)
            frame.pack(pady=5, padx=20, fill='x')
            tk.Label(frame, text=label, width=12, anchor='w').pack(side='left')

            if key == 'description':
                entry = tk.Text(frame, height=5, width=30)
                entry.pack(side='left', fill='x', expand=True)
            else:
                entry = tk.Entry(frame, width=30)
                entry.pack(side='left', fill='x', expand=True)
            entries[key] = entry

        def save():
            name = entries['name'].get().strip()
            location = entries['location'].get().strip()
            description = entries['description'].get('1.0', 'end-1c').strip()

            if not name or not location:
                messagebox.showerror("错误", "景点名和地理位置不能为空！")
                return

            try:
                self.db.create_place(name, location, description)
                messagebox.showinfo("成功", "景点添加成功！")
                dialog.destroy()
                self.load_places()
            except Exception as e:
                messagebox.showerror("错误", f"添加失败：{str(e)}")

        tk.Button(dialog, text="保存", command=save, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 10)).pack(pady=20)

    def edit_place(self):
        """编辑景点"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要编辑的景点！")
            return

        values = self.tree.item(selected[0])['values']
        place_id = values[0]
        place = self.db.get_place_by_id(place_id)

        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑景点")
        dialog.geometry("400x450")

        tk.Label(dialog, text="编辑景点信息", font=("微软雅黑", 14, "bold")).pack(pady=10)

        fields = [("景点名:", place['name']), ("地理位置:", place['location'])]
        entries = {}

        for label, value in fields:
            frame = tk.Frame(dialog)
            frame.pack(pady=5, padx=20, fill='x')
            tk.Label(frame, text=label, width=12, anchor='w').pack(side='left')
            entry = tk.Entry(frame, width=30)
            entry.insert(0, value)
            entry.pack(side='left', fill='x', expand=True)
            entries[label] = entry

        # 描述用文本框
        frame = tk.Frame(dialog)
        frame.pack(pady=5, padx=20, fill='x')
        tk.Label(frame, text="红色历史:", width=12, anchor='w').pack(side='left')
        desc_text = tk.Text(frame, height=5, width=30)
        desc_text.insert('1.0', place['description'])
        desc_text.pack(side='left', fill='x', expand=True)

        def save():
            name = entries['景点名:'].get().strip()
            location = entries['地理位置:'].get().strip()
            description = desc_text.get('1.0', 'end-1c').strip()

            if not name or not location:
                messagebox.showerror("错误", "景点名和地理位置不能为空！")
                return

            try:
                self.db.update_place(place_id, name=name, location=location, description=description)
                messagebox.showinfo("成功", "景点更新成功！")
                dialog.destroy()
                self.load_places()
            except Exception as e:
                messagebox.showerror("错误", f"更新失败：{str(e)}")

        tk.Button(dialog, text="保存", command=save, bg="#4CAF50", fg="white",
                  font=("微软雅黑", 10)).pack(pady=20)

    def delete_place(self):
        """删除景点"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的景点！")
            return

        if not messagebox.askyesno("确认", "确定要删除该景点吗？\n删除后不可恢复！"):
            return

        values = self.tree.item(selected[0])['values']
        place_id = values[0]

        try:
            self.db.delete_place(place_id)
            messagebox.showinfo("成功", "景点删除成功！")
            self.load_places()
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")


class HotPlaceView:
    """热门景点排行榜"""

    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_widgets()
        self.load_hot_places()

    def create_widgets(self):
        """创建界面组件"""
        tk.Label(self.parent, text="⭐ 热门景点排行榜", font=("微软雅黑", 18, "bold"),
                 fg="#FF6B00", bg="white").pack(pady=(10, 15))

        tk.Label(self.parent, text="打卡次数 ≥ 10 次自动成为热门景点",
                 font=("微软雅黑", 10), fg="#666", bg="white").pack()

        tree_frame = tk.Frame(self.parent, bg="white")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('排名', '景点名', '地理位置', '打卡次数', '热门程度')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        col_widths = [60, 180, 180, 100, 100]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def load_hot_places(self):
        """加载热门景点"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        places = self.db.get_top_hot_places(limit=10)

        for idx, place in enumerate(places, 1):
            hot_level = '🔥🔥🔥' if place['checkin_count'] >= 50 else '🔥🔥' if place['checkin_count'] >= 30 else '🔥'
            self.tree.insert('', 'end', values=(
                f'#{idx}',
                place['name'],
                place['location'],
                place['checkin_count'],
                hot_level
            ))

            if idx <= 3:
                self.tree.tag_configure(f'rank_{idx}', background='#FFFACD')
                self.tree.item(self.tree.get_children()[-1], tags=(f'rank_{idx}',))