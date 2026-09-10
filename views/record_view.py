"""
打卡记录管理界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class RecordView:
    def __init__(self, parent, db, user_id, refresh_callback=None):
        self.parent = parent
        self.db = db
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.create_widgets()
        self.load_records()

    def create_widgets(self):
        """创建界面组件"""
        tk.Label(self.parent, text="📝 我的打卡记录", font=("微软雅黑", 18, "bold"),
                 bg="white").pack(pady=(10, 15))

        # 操作栏
        control_frame = tk.Frame(self.parent, bg="white")
        control_frame.pack(pady=5, padx=20, fill='x')

        tk.Button(control_frame, text="🔄 刷新", command=self.load_records).pack(side='left', padx=5)
        tk.Button(control_frame, text="📍 去打卡", bg="#4CAF50", fg="white",
                  command=self.show_checkin_dialog).pack(side='left', padx=5)

        # 排序
        tk.Label(control_frame, text="排序:", bg="white").pack(side='left', padx=(20, 5))
        self.sort_var = tk.StringVar(value="时间降序")
        sort_combo = ttk.Combobox(control_frame, textvariable=self.sort_var,
                                  values=["时间降序", "时间升序", "景点名"], width=12)
        sort_combo.pack(side='left', padx=5)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.load_records())

        # 搜索
        tk.Label(control_frame, text="景点ID:", bg="white").pack(side='left', padx=(20, 5))
        self.search_entry = tk.Entry(control_frame, width=10)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(control_frame, text="按景点查询", command=self.search_by_place).pack(side='left', padx=5)

        # 打卡记录列表
        tree_frame = tk.Frame(self.parent, bg="white")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('记录ID', '景点名', '地理位置', '打卡时间', '心得')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        col_widths = [60, 150, 150, 150, 300]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='w')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<Double-Button-1>', self.view_record_detail)

        # 操作按钮
        btn_frame = tk.Frame(self.parent, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="修改心得", command=self.edit_record).pack(side='left', padx=5)
        tk.Button(btn_frame, text="删除记录", command=self.delete_record,
                  bg="#FF6B6B", fg="white").pack(side='left', padx=5)

    def load_records(self):
        """加载打卡记录"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = self.db.get_records_by_user(self.user_id)
        sort_type = self.sort_var.get()

        if sort_type == "时间升序":
            records = sorted(records, key=lambda x: x['checkin_time'])
        elif sort_type == "景点名":
            records = sorted(records, key=lambda x: x['place_name'])

        for rec in records:
            self.tree.insert('', 'end', values=(
                rec['id'],
                rec['place_name'],
                rec['location'],
                rec['checkin_time'][:19] if rec['checkin_time'] else '',
                rec['experience'][:30] + ('...' if len(rec['experience']) > 30 else '') if rec['experience'] else ''
            ))

    def search_by_place(self):
        """按景点ID查询打卡记录"""
        place_id = self.search_entry.get().strip()
        if not place_id.isdigit():
            messagebox.showerror("错误", "请输入有效的景点ID！")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        results = self.db.get_records_by_place(int(place_id))
        results = [r for r in results if r['user_id'] == self.user_id]

        if not results:
            messagebox.showinfo("提示", "未找到该景点的打卡记录！")
            return

        for rec in results:
            self.tree.insert('', 'end', values=(
                rec['id'],
                rec.get('place_name', '未知景点'),
                rec.get('location', ''),
                rec['checkin_time'][:19] if rec['checkin_time'] else '',
                rec['experience'][:30] + ('...' if len(rec['experience']) > 30 else '') if rec['experience'] else ''
            ))

    def view_record_detail(self, event):
        """查看打卡详情"""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        record_id = values[0]
        rec = self.db.get_record_by_id(record_id)
        if not rec:
            return

        detail_win = tk.Toplevel(self.parent)
        detail_win.title("打卡详情")
        detail_win.geometry("500x350")

        tk.Label(detail_win, text=f"📝 打卡详情", font=("微软雅黑", 16, "bold"),
                 fg="#8B0000").pack(pady=10)

        info = f"""
        记录ID: {rec['id']}
        景点名: {rec['place_name']}
        地理位置: {rec['location']}
        打卡时间: {rec['checkin_time']}
        打卡心得: 
        """
        tk.Label(detail_win, text=info, font=("微软雅黑", 11), justify='left').pack(pady=5, padx=20, anchor='w')

        text_area = scrolledtext.ScrolledText(detail_win, height=5, font=("微软雅黑", 10))
        text_area.pack(pady=5, padx=20, fill='both', expand=True)
        text_area.insert('1.0', rec['experience'] or '（未填写心得）')
        text_area.config(state='disabled')

    def show_checkin_dialog(self):
        """打卡对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("📍 打卡")
        dialog.geometry("400x350")

        tk.Label(dialog, text="📍 红色文化打卡", font=("微软雅黑", 16, "bold"),
                 fg="#8B0000").pack(pady=10)

        # 选择景点
        tk.Label(dialog, text="选择景点:", font=("微软雅黑", 11)).pack(anchor='w', padx=20)
        places = self.db.get_all_places()
        place_names = [f"{p['id']}. {p['name']}" for p in places]

        self.place_combo = ttk.Combobox(dialog, values=place_names, width=35, state='readonly')
        self.place_combo.pack(pady=5, padx=20, fill='x')
        if place_names:
            self.place_combo.current(0)

        # 打卡心得
        tk.Label(dialog, text="打卡心得:", font=("微软雅黑", 11)).pack(anchor='w', padx=20, pady=(10, 0))
        experience_text = scrolledtext.ScrolledText(dialog, height=4, font=("微软雅黑", 10))
        experience_text.pack(pady=5, padx=20, fill='x')

        def do_checkin():
            if not self.place_combo.get():
                messagebox.showerror("错误", "请选择要打卡的景点！")
                return

            place_id = int(self.place_combo.get().split('.')[0])
            experience = experience_text.get('1.0', 'end-1c').strip()

            try:
                self.db.create_record(self.user_id, place_id, experience)
                messagebox.showinfo("成功", "✅ 打卡成功！学习积分 +1")
                dialog.destroy()
                self.load_records()
                if self.refresh_callback:
                    self.refresh_callback()
            except ValueError as e:
                messagebox.showerror("提示", str(e))
            except Exception as e:
                messagebox.showerror("错误", f"打卡失败：{str(e)}")

        tk.Button(dialog, text="✅ 确认打卡", command=do_checkin,
                  bg="#4CAF50", fg="white", font=("微软雅黑", 11, "bold"),
                  width=20).pack(pady=20)

    def edit_record(self):
        """修改打卡心得"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要修改的打卡记录！")
            return

        values = self.tree.item(selected[0])['values']
        record_id = values[0]
        rec = self.db.get_record_by_id(record_id)

        dialog = tk.Toplevel(self.parent)
        dialog.title("修改打卡心得")
        dialog.geometry("400x250")

        tk.Label(dialog, text="修改打卡心得", font=("微软雅黑", 14, "bold")).pack(pady=10)

        tk.Label(dialog, text=f"景点: {rec['place_name']}", font=("微软雅黑", 10)).pack()

        tk.Label(dialog, text="新心得:", font=("微软雅黑", 10)).pack(anchor='w', padx=20, pady=(10, 0))
        text_area = scrolledtext.ScrolledText(dialog, height=4, font=("微软雅黑", 10))
        text_area.pack(pady=5, padx=20, fill='x')
        text_area.insert('1.0', rec['experience'] or '')

        def save():
            new_experience = text_area.get('1.0', 'end-1c').strip()
            try:
                self.db.update_record_experience(record_id, new_experience)
                messagebox.showinfo("成功", "心得修改成功！")
                dialog.destroy()
                self.load_records()
            except Exception as e:
                messagebox.showerror("错误", f"修改失败：{str(e)}")

        tk.Button(dialog, text="保存", command=save, bg="#4CAF50", fg="white").pack(pady=15)

    def delete_record(self):
        """删除打卡记录"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的打卡记录！")
            return

        if not messagebox.askyesno("确认", "确定要删除该打卡记录吗？\n删除后学习积分将 -1！"):
            return

        values = self.tree.item(selected[0])['values']
        record_id = values[0]

        try:
            self.db.delete_record(record_id)
            messagebox.showinfo("成功", "打卡记录已删除，学习积分 -1")
            self.load_records()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")