#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
浏览器启动管理器
功能：读取配置文件，通过可视化面板管理浏览器启动
"""

import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import shutil

# 配置文件路径
CONFIG_FILE = "browser_configs.json"


class BrowserManager:
    def __init__(self, root):
        self.root = root
        self.root.title("浏览器启动管理器")
        self.root.geometry("900x650")
        
        # 加载配置
        self.configs = self.load_configs()
        
        # 构建UI
        self.setup_ui()
        
        # 刷新树形视图
        self.refresh_tree()
    
    def load_configs(self):
        """加载配置文件"""
        if not os.path.exists(CONFIG_FILE):
            # 如果配置文件不存在，创建空配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return []
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("错误", "配置文件格式错误！")
            return []
    
    def save_configs(self):
        """保存配置文件"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.configs, f, ensure_ascii=False, indent=2)
    
    def setup_ui(self):
        """构建UI界面"""
        # 主框架 - 左右分割
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧 - 树形面板
        left_frame = ttk.Frame(main_frame, width=350)
        main_frame.add(left_frame, weight=1)
        
        # 树形视图
        tree_scroll = ttk.Scrollbar(left_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(left_frame, yscrollcommand=tree_scroll.set, selectmode='browse')
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)
        
        # 绑定事件
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # 左侧按钮区域
        left_btn_frame = ttk.Frame(left_frame)
        left_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(left_btn_frame, text="新建配置", command=self.new_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_btn_frame, text="刷新", command=self.refresh_tree).pack(side=tk.LEFT, padx=2)
        
        # 右侧 - 详情面板
        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=2)
        
        # 详情文本区域
        ttk.Label(right_frame, text="配置详情:").pack(anchor=tk.W)
        
        self.detail_text = scrolledtext.ScrolledText(right_frame, height=20, font=("Consolas", 10))
        self.detail_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 右侧按钮区域
        right_btn_frame = ttk.Frame(right_frame)
        right_btn_frame.pack(fill=tk.X)
        
        ttk.Button(right_btn_frame, text="启动浏览器", command=self.launch_browser).pack(side=tk.LEFT, padx=2)
        ttk.Button(right_btn_frame, text="编辑配置", command=self.edit_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(right_btn_frame, text="创建副本", command=self.duplicate_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(right_btn_frame, text="移动分组", command=self.move_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(right_btn_frame, text="删除配置", command=self.delete_config).pack(side=tk.LEFT, padx=2)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 当前选中项
        self.current_item = None
        self.current_config = None
    
    def build_group_tree(self):
        """构建分组树形结构"""
        tree_data = {}
        
        for config in self.configs:
            group = config.get("group", "未分组")
            name = config.get("name", "")
            parts = group.split("/")
            
            # 构建树形结构
            current = tree_data
            for i, part in enumerate(parts):
                if part not in current:
                    if i == len(parts) - 1:
                        # 最后一级分组，存储配置列表
                        current[part] = {"_configs": []}
                    else:
                        current[part] = {}
                # 如果不是叶子节点标记，添加配置
                if "_configs" in current[part]:
                    current[part]["_configs"].append(name)
                else:
                    # 中间层级，确保是字典
                    if not isinstance(current[part], dict):
                        current[part] = {}
                current = current[part]
        
        return tree_data
    
    def refresh_tree(self):
        """刷新树形视图"""
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 重新加载配置
        self.configs = self.load_configs()
        
        # 构建树形结构
        tree_data = self.build_group_tree()
        
        # 递归插入节点
        self.insert_tree_nodes("", tree_data, [])
        
        self.status_var.set(f"已加载 {len(self.configs)} 个配置")
    
    def insert_tree_nodes(self, parent, nodes, path):
        """递归插入树节点"""
        # 获取当前层级的所有配置名称并排序
        config_names = nodes.get("_configs", [])
        for name in sorted(config_names):
            full_path = "/".join(path) if path else "未分组"
            node_id = self.tree.insert(parent, 'end', text=f"🌐 {name}", tags=('config',), values=(full_path,))
        
        # 获取分组节点并排序（排除 _configs 特殊键）
        group_names = [k for k in nodes.keys() if not k.startswith("_")]
        for name in sorted(group_names):
            children = nodes[name]
            full_path = "/".join(path + [name])
            
            if isinstance(children, dict) and children:
                # 有子节点，创建文件夹节点
                node_id = self.tree.insert(parent, 'end', text=f"📁 {name}", open=False, tags=('group',))
                self.insert_tree_nodes(node_id, children, path + [name])
            elif isinstance(children, dict) and not children:
                # 空文件夹
                node_id = self.tree.insert(parent, 'end', text=f"📁 {name}", open=False, tags=('group',))
            else:
                # 叶子节点 - 配置项
                node_id = self.tree.insert(parent, 'end', text=f"🌐 {name}", tags=('config',), values=(full_path,))
    
    def find_configs_by_group(self, group_path):
        """根据分组路径查找配置"""
        return [c for c in self.configs if c.get("group") == group_path]
    
    def on_select(self, event):
        """选中事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        tags = self.tree.item(item_id, 'tags')
        
        if 'config' in tags:
            # 选中了配置项
            values = self.tree.item(item_id, 'values')
            group_path = values[0] if values else ""
            name = self.tree.item(item_id, 'text').replace("🌐 ", "")
            
            # 查找对应的配置
            configs = self.find_configs_by_group(group_path)
            for config in configs:
                if config.get("name") == name:
                    self.current_item = item_id
                    self.current_config = config
                    self.show_config_detail(config)
                    break
        else:
            self.current_item = None
            self.current_config = None
            self.detail_text.delete(1.0, tk.END)
    
    def on_double_click(self, event):
        """双击事件 - 启动浏览器"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        tags = self.tree.item(item_id, 'tags')
        
        if 'config' in tags and self.current_config:
            self.launch_browser()
    
    def show_config_detail(self, config):
        """显示配置详情"""
        self.detail_text.delete(1.0, tk.END)
        detail = json.dumps(config, ensure_ascii=False, indent=2)
        self.detail_text.insert(tk.END, detail)
    
    def launch_browser(self):
        """启动浏览器"""
        if not self.current_config:
            messagebox.showwarning("警告", "请先选择一个配置项！")
            return
        
        config = self.current_config
        
        # 构建启动命令
        cmd = [config.get("browser_path", "")]
        
        # 添加参数
        if config.get("user_data_dir"):
            cmd.append(f'--user-data-dir={config["user_data_dir"]}')
        
        if config.get("profile_directory"):
            cmd.append(f'--profile-directory={config["profile_directory"]}')
        
        if config.get("proxy_server"):
            cmd.append(f'--proxy-server={config["proxy_server"]}')
        
        if config.get("disable_plugins"):
            cmd.append("--disable-plugins")
        
        if config.get("incognito"):
            if "chrome" in config.get("browser_path", "").lower() or "chromium" in config.get("browser_path", "").lower():
                cmd.append("--incognito")
            else:
                cmd.append("-private")
        
        if config.get("app"):
            cmd.append(f'--app={config["app"]}')
        
        if config.get("extra_params"):
            cmd.extend(config["extra_params"].split())
        
        try:
            subprocess.Popen(cmd)
            self.status_var.set(f"已启动: {config.get('name', '未知')}")
        except FileNotFoundError:
            messagebox.showerror("错误", f"找不到浏览器程序: {config.get('browser_path')}")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")
    
    def get_selected_config_name(self):
        """获取选中配置的名称"""
        if not self.current_item:
            return None
        return self.tree.item(self.current_item, 'text').replace("🌐 ", "")
    
    def edit_config(self):
        """编辑配置"""
        if not self.current_config:
            messagebox.showwarning("警告", "请先选择一个配置项！")
            return
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑配置: {self.current_config.get('name')}")
        edit_window.geometry("600x500")
        
        # JSON编辑区域
        ttk.Label(edit_window, text="编辑配置 (JSON格式):").pack(anchor=tk.W, padx=10, pady=5)
        
        json_text = scrolledtext.ScrolledText(edit_window, height=25, font=("Consolas", 10))
        json_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 填充当前配置
        json_text.insert(tk.END, json.dumps(self.current_config, ensure_ascii=False, indent=2))
        
        # 按钮区域
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_edit():
            try:
                new_config = json.loads(json_text.get(1.0, tk.END))
                
                # 验证必要字段
                if "name" not in new_config:
                    messagebox.showerror("错误", "配置必须包含 'name' 字段！")
                    return
                
                # 查找原配置索引
                old_name = self.current_config.get("name")
                old_group = self.current_config.get("group")
                
                for i, config in enumerate(self.configs):
                    if config.get("name") == old_name and config.get("group") == old_group:
                        self.configs[i] = new_config
                        break
                
                self.save_configs()
                self.refresh_tree()
                edit_window.destroy()
                self.status_var.set(f"已更新配置: {new_config.get('name')}")
                messagebox.showinfo("成功", "配置已更新！")
                
            except json.JSONDecodeError as e:
                messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
        
        ttk.Button(btn_frame, text="保存", command=save_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def new_config(self):
        """新建配置"""
        # 创建新建窗口
        new_window = tk.Toplevel(self.root)
        new_window.title("新建配置")
        new_window.geometry("600x500")
        
        # JSON编辑区域
        ttk.Label(new_window, text="输入配置 (JSON格式):").pack(anchor=tk.W, padx=10, pady=5)
        
        # 默认模板
        template = {
            "name": "新配置",
            "group": "未分组",
            "browser_path": "",
            "user_data_dir": "",
            "profile_directory": "",
            "proxy_server": "",
            "disable_plugins": False,
            "incognito": False,
            "app": "",
            "extra_params": ""
        }
        
        json_text = scrolledtext.ScrolledText(new_window, height=25, font=("Consolas", 10))
        json_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        json_text.insert(tk.END, json.dumps(template, ensure_ascii=False, indent=2))
        
        # 按钮区域
        btn_frame = ttk.Frame(new_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_new():
            try:
                new_config = json.loads(json_text.get(1.0, tk.END))
                
                # 验证必要字段
                if "name" not in new_config:
                    messagebox.showerror("错误", "配置必须包含 'name' 字段！")
                    return
                
                # 检查名称是否已存在
                for config in self.configs:
                    if config.get("name") == new_config.get("name") and config.get("group") == new_config.get("group"):
                        messagebox.showerror("错误", f"该分组下已存在名为 '{new_config.get('name')}' 的配置！")
                        return
                
                self.configs.append(new_config)
                self.save_configs()
                self.refresh_tree()
                new_window.destroy()
                self.status_var.set(f"已新建配置: {new_config.get('name')}")
                messagebox.showinfo("成功", "配置已创建！")
                
            except json.JSONDecodeError as e:
                messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
        
        ttk.Button(btn_frame, text="创建", command=save_new).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=new_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def duplicate_config(self):
        """创建副本"""
        if not self.current_config:
            messagebox.showwarning("警告", "请先选择一个配置项！")
            return
        
        # 创建副本窗口
        dup_window = tk.Toplevel(self.root)
        dup_window.title(f"创建副本: {self.current_config.get('name')}")
        dup_window.geometry("600x500")
        
        # 创建副本配置
        dup_config = self.current_config.copy()
        dup_config["name"] = f"{dup_config['name']}_副本"
        
        # JSON编辑区域
        ttk.Label(dup_window, text="编辑副本配置 (JSON格式):").pack(anchor=tk.W, padx=10, pady=5)
        
        json_text = scrolledtext.ScrolledText(dup_window, height=25, font=("Consolas", 10))
        json_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        json_text.insert(tk.END, json.dumps(dup_config, ensure_ascii=False, indent=2))
        
        # 按钮区域
        btn_frame = ttk.Frame(dup_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_duplicate():
            try:
                new_config = json.loads(json_text.get(1.0, tk.END))
                
                # 验证必要字段
                if "name" not in new_config:
                    messagebox.showerror("错误", "配置必须包含 'name' 字段！")
                    return
                
                # 检查名称是否已存在
                for config in self.configs:
                    if config.get("name") == new_config.get("name") and config.get("group") == new_config.get("group"):
                        messagebox.showerror("错误", f"该分组下已存在名为 '{new_config.get('name')}' 的配置！")
                        return
                
                self.configs.append(new_config)
                self.save_configs()
                self.refresh_tree()
                dup_window.destroy()
                self.status_var.set(f"已创建副本: {new_config.get('name')}")
                messagebox.showinfo("成功", "副本已创建！")
                
            except json.JSONDecodeError as e:
                messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
        
        ttk.Button(btn_frame, text="创建副本", command=save_duplicate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dup_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def move_config(self):
        """移动配置到新的分组"""
        if not self.current_config:
            messagebox.showwarning("警告", "请先选择一个配置项！")
            return
        
        config = self.current_config
        config_name = config.get("name", "未知")
        current_group = config.get("group", "")
        
        # 创建移动窗口
        move_window = tk.Toplevel(self.root)
        move_window.title(f"移动配置: {config_name}")
        move_window.geometry("400x200")
        
        ttk.Label(move_window, text="目标分组路径 (使用 / 分隔):").pack(anchor=tk.W, padx=10, pady=10)
        group_entry = ttk.Entry(move_window, width=50)
        group_entry.pack(padx=10, pady=5)
        group_entry.insert(0, current_group)
        
        def do_move():
            new_group = group_entry.get().strip()
            if not new_group:
                messagebox.showerror("错误", "分组路径不能为空！")
                return
            
            # 更新配置
            config["group"] = new_group
            self.save_configs()
            self.refresh_tree()
            move_window.destroy()
            self.status_var.set(f"已移动配置到: {new_group}")
            messagebox.showinfo("成功", f"配置已移动到: {new_group}")
        
        btn_frame = ttk.Frame(move_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="移动", command=do_move).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=move_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_config(self):
        """删除配置"""
        if not self.current_config:
            messagebox.showwarning("警告", "请先选择一个配置项！")
            return
        
        config = self.current_config
        name = config.get("name", "未知")
        group = config.get("group", "")
        
        if messagebox.askyesno("确认删除", f"确定要删除配置 '{name}' 吗？"):
            
            self.configs = [c for c in self.configs if not (c.get("name") == name and c.get("group") == group)]
            self.save_configs()
            self.refresh_tree()
            self.current_config = None
            self.detail_text.delete(1.0, tk.END)
            self.status_var.set(f"已删除配置: {name}")
            messagebox.showinfo("成功", "配置已删除！")


def main():
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    try:
        style.theme_use('vista')  # Windows
    except:
        try:
            style.theme_use('clam')  # Linux/Mac
        except:
            pass
    
    app = BrowserManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
