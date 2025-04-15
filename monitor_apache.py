import tkinter as tk
import os
from datetime import datetime
from threading import Thread
from pystray import Icon as TrayIcon, MenuItem as item, Menu
from PIL import Image
import sys

LOG_PATH = r"C:\xampp\apache_monitor_log.txt"
UPDATE_INTERVAL = 5000  # 5 segundos

def resource_path(relative_path):
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class ApacheMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitor de Apache - XAMPP")
        self.root.geometry("600x300")
        self.root.configure(bg="#f2f2f2")
        self.root.resizable(False, False)

        # Remove botão de fechar e permite mover a janela
        self.root.overrideredirect(True)
        self.root.bind("<B1-Motion>", self.mover_janela)
        self.root.bind("<Button-1>", self.iniciar_movimento)

        self._offsetx = 0
        self._offsety = 0

        self.setup_ui()
        self.update_log()

        # Minimizar para bandeja
        self.root.protocol("WM_DELETE_WINDOW", self.minimizar_para_bandeja)

        # Carrega o ícone usando resource_path
        self.icon_image = Image.open(resource_path("favicon.ico"))

        self.tray_icon = TrayIcon("ApacheMonitor", self.icon_image, menu=Menu(
            item("Restaurar", self.restaurar_janela),
            item("Sair", self.fechar_app)
        ))

        self.tray_thread = Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

        self.root.mainloop()

    def mover_janela(self, event):
        x = event.x_root - self._offsetx
        y = event.y_root - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def iniciar_movimento(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="📊 Monitor de Serviço Apache", font=("Segoe UI", 18, "bold"), bg="#f2f2f2", fg="#333")
        self.title_label.pack(pady=(20, 10))
        self.title_label.bind("<Double-Button-1>", self.minimizar_para_bandeja)  # Duplo clique só no título

        self.lbl_quedas = tk.Label(self.root, text="", font=("Segoe UI", 14), bg="#f2f2f2", fg="#cc0000")
        self.lbl_quedas.pack(pady=5)

        self.lbl_subidas = tk.Label(self.root, text="", font=("Segoe UI", 14), bg="#f2f2f2", fg="#006600")
        self.lbl_subidas.pack(pady=5)

        self.lbl_ultima_queda = tk.Label(self.root, text="", font=("Segoe UI", 12), bg="#f2f2f2", fg="#333")
        self.lbl_ultima_queda.pack(pady=5)

        self.lbl_ultima_subida = tk.Label(self.root, text="", font=("Segoe UI", 12), bg="#f2f2f2", fg="#333")
        self.lbl_ultima_subida.pack(pady=5)

        self.lbl_ultima_atualizacao = tk.Label(self.root, text="", font=("Segoe UI", 10, "italic"), bg="#f2f2f2", fg="#666")
        self.lbl_ultima_atualizacao.pack(pady=(15, 0))

    def update_log(self):
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r", encoding="utf-8") as file:
                linhas = file.readlines()

            quedas = [linha for linha in linhas if "Apache caiu" in linha]
            subidas = [linha for linha in linhas if "Apache reiniciado com sucesso" in linha]

            self.lbl_quedas.config(text=f"⚠️ Total de quedas: {len(quedas)}")
            self.lbl_subidas.config(text=f"✅ Total de reinícios: {len(subidas)}")

            ultima_queda = self.formatar_data(quedas[-1]) if quedas else "N/A"
            ultima_subida = self.formatar_data(subidas[-1]) if subidas else "N/A"

            self.lbl_ultima_queda.config(text=f"Última queda: {ultima_queda}")
            self.lbl_ultima_subida.config(text=f"Último reinício: {ultima_subida}")
        else:
            self.lbl_quedas.config(text="Arquivo de log não encontrado.")
            self.lbl_subidas.config(text="")
            self.lbl_ultima_queda.config(text="")
            self.lbl_ultima_subida.config(text="")

        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lbl_ultima_atualizacao.config(text=f"Última atualização: {agora}")

        self.root.after(UPDATE_INTERVAL, self.update_log)

    def formatar_data(self, linha):
        try:
            data_str = linha.split(" - ")[0].strip()
            # Tenta primeiro o formato brasileiro, depois o americano
            try:
                data = datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            return data.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return linha.strip()

    def minimizar_para_bandeja(self, event=None):
        self.root.withdraw()

    def restaurar_janela(self, icon=None, item=None):
        self.root.deiconify()

    def fechar_app(self, icon=None, item=None):
        self.tray_icon.stop()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    ApacheMonitorApp()
