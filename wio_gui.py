import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from wio_reduce import reduce_main
import argparse


class ImageOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web画像最適化ツール")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="Web画像最適化ツール", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Label(main_frame, text="対象パス *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="参照", command=self.browse_path).grid(row=1, column=2, padx=(5, 0), pady=5)
        
        ttk.Label(main_frame, text="目標サイズ (KB) *:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.size_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.size_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        ttk.Label(main_frame, text="最大幅 (px):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.width_var, width=20).grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        ttk.Label(main_frame, text="最大高さ (px):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.height_var, width=20).grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        ttk.Label(main_frame, text="JPEG品質 (1-100):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value="85")
        ttk.Entry(main_frame, textvariable=self.quality_var, width=20).grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        options_frame = ttk.LabelFrame(main_frame, text="オプション", padding="10")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(0, weight=1)
        
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="ディレクトリを再帰的に処理", variable=self.recursive_var).grid(row=0, column=0, sticky=tk.W)
        
        self.nobackup_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="バックアップをスキップ", variable=self.nobackup_var).grid(row=1, column=0, sticky=tk.W)
        
        self.parallel_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="並列処理を有効化", variable=self.parallel_var).grid(row=2, column=0, sticky=tk.W)
        
        self.webp_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="WebP形式に変換", variable=self.webp_var).grid(row=3, column=0, sticky=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="処理開始", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="クリア", command=self.clear_fields).pack(side=tk.LEFT)
        
        self.progress_var = tk.StringVar(value="準備完了")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=8, column=0, columnspan=3, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        
        output_frame = ttk.LabelFrame(main_frame, text="出力", padding="5")
        output_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        
        self.output_text = tk.Text(output_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_path(self):
        path = filedialog.askdirectory() or filedialog.askopenfilename(
            filetypes=[("画像ファイル", "*.jpg *.jpeg *.png"), ("すべてのファイル", "*.*")]
        )
        if path:
            self.path_var.set(path)
    
    def clear_fields(self):
        self.path_var.set("")
        self.size_var.set("")
        self.width_var.set("")
        self.height_var.set("")
        self.quality_var.set("85")
        self.recursive_var.set(False)
        self.nobackup_var.set(False)
        self.parallel_var.set(False)
        self.webp_var.set(False)
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set("準備完了")
        
    def validate_input(self):
        if not self.path_var.get().strip():
            messagebox.showerror("エラー", "対象パスを選択してください")
            return False
            
        if not self.size_var.get().strip():
            messagebox.showerror("エラー", "目標サイズをKBで入力してください")
            return False
            
        try:
            size = int(self.size_var.get())
            if size <= 0:
                messagebox.showerror("エラー", "目標サイズは正の数である必要があります")
                return False
        except ValueError:
            messagebox.showerror("エラー", "目標サイズは有効な数値である必要があります")
            return False
            
        if self.width_var.get().strip():
            try:
                width = int(self.width_var.get())
                if width <= 0:
                    messagebox.showerror("エラー", "幅は正の数である必要があります")
                    return False
            except ValueError:
                messagebox.showerror("エラー", "幅は有効な数値である必要があります")
                return False
                
        if self.height_var.get().strip():
            try:
                height = int(self.height_var.get())
                if height <= 0:
                    messagebox.showerror("エラー", "高さは正の数である必要があります")
                    return False
            except ValueError:
                messagebox.showerror("エラー", "高さは有効な数値である必要があります")
                return False
                
        try:
            quality = int(self.quality_var.get())
            if not (1 <= quality <= 100):
                messagebox.showerror("エラー", "JPEG品質は1から100の間である必要があります")
                return False
        except ValueError:
            messagebox.showerror("エラー", "JPEG品質は有効な数値である必要があります")
            return False
            
        return True
        
    def start_processing(self):
        if not self.validate_input():
            return
            
        self.process_button.config(state="disabled")
        self.progress_bar.start()
        self.progress_var.set("処理中...")
        self.output_text.delete(1.0, tk.END)
        
        threading.Thread(target=self.process_images, daemon=True).start()
        
    def process_images(self):
        try:
            args = argparse.Namespace()
            args.path = self.path_var.get().strip()
            args.size = int(self.size_var.get())
            args.width = int(self.width_var.get()) if self.width_var.get().strip() else None
            args.height = int(self.height_var.get()) if self.height_var.get().strip() else None
            args.quality = int(self.quality_var.get())
            args.recursive = self.recursive_var.get()
            args.nobackup = self.nobackup_var.get()
            args.backup = not args.nobackup
            args.parallel = self.parallel_var.get()
            args.webp = self.webp_var.get()
            args.command = "reduce"
            
            import sys
            import io
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            captured_output = io.StringIO()
            sys.stdout = captured_output
            sys.stderr = captured_output
            
            try:
                reduce_main(args)
                result = captured_output.getvalue()
                
                self.root.after(0, lambda: self.update_output(result, True))
                
            except Exception as e:
                error_msg = f"Error: {str(e)}\n{captured_output.getvalue()}"
                self.root.after(0, lambda: self.update_output(error_msg, False))
                
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.root.after(0, lambda: self.update_output(error_msg, False))
            
    def update_output(self, text, success):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        
        self.progress_bar.stop()
        self.process_button.config(state="normal")
        
        if success:
            self.progress_var.set("処理が正常に完了しました！")
            messagebox.showinfo("成功", "画像処理が正常に完了しました！")
        else:
            self.progress_var.set("処理が失敗しました！")
            messagebox.showerror("エラー", "画像処理が失敗しました。詳細は出力を確認してください。")


def main():
    root = tk.Tk()
    app = ImageOptimizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()