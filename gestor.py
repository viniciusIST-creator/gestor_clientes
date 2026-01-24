import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import calendar

ARQUIVO = "dados.json"


# =================== UTIL ===================
def data_str_para_date(s):
    return datetime.strptime(s, "%d/%m/%y").date()


# =================== DADOS ===================
def carregar():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for cliente, itens in dados.items():
        for nome, valor in list(itens.items()):
            if isinstance(valor, bool):
                itens[nome] = {"feito": valor, "data": None}
    return dados


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# =================== APP ===================
class GestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de engenharia - feito por Vinicius Coelho")
        self.root.geometry("1400x650")
        self.root.configure(bg="white")

        self.dados = carregar()
        self.cliente_atual = None
        self.item_selecionado = None
        self.check_vars = {}
        self.filtro_atual = "Todas"

        hoje = date.today()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year

        self.configurar_estilo()
        self.build_ui()
        self.atualizar_lista()

    # =================== ESTILO ===================
    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")

        azul = "#0b3c6f"
        azul_claro = "#dbe9f6"

        style.configure("TLabel", background="white", foreground="black")
        style.configure("Header.TLabel",
                        font=("Segoe UI", 12, "bold"),
                        foreground=azul,
                        background="white")

        style.configure("Treeview",
                        background="white",
                        fieldbackground="white",
                        foreground="black",
                        rowheight=26)
        style.map("Treeview",
                  background=[("selected", azul)],
                  foreground=[("selected", "white")])

        style.configure("TFrame", background="white")
        style.configure("Selected.TFrame", background=azul_claro)

    # =================== UI ===================
    def build_ui(self):
        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.middle = ttk.Frame(self.root, padding=10)
        self.middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH)

        ttk.Label(self.right, text="Calendário", style="Header.TLabel").pack(anchor="w")

        self.frame_cal = ttk.Frame(self.right)
        self.frame_cal.pack(fill=tk.X, pady=6)

        self.mostrar_calendario()

    # =================== CALENDÁRIO ===================
    def mostrar_calendario(self):
        for w in self.frame_cal.winfo_children():
            w.destroy()

        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        # ===== CONTROLES DE MÊS E ANO =====
        controles = ttk.Frame(self.frame_cal)
        controles.pack(pady=4)

        ttk.Label(controles, text="Mês:").pack(side=tk.LEFT, padx=(0, 4))

        cb_mes = ttk.Combobox(
            controles,
            values=meses,
            state="readonly",
            width=12
        )
        cb_mes.current(self.mes_atual - 1)
        cb_mes.pack(side=tk.LEFT)

        ttk.Label(controles, text="Ano:").pack(side=tk.LEFT, padx=(10, 4))

        sp_ano = tk.Spinbox(
            controles,
            from_=2000,
            to=2100,
            width=6
        )
        sp_ano.delete(0, tk.END)
        sp_ano.insert(0, self.ano_atual)
        sp_ano.pack(side=tk.LEFT)

        def atualizar_calendario(*_):
            self.mes_atual = cb_mes.current() + 1
            self.ano_atual = int(sp_ano.get())
            self.mostrar_calendario()

        cb_mes.bind("<<ComboboxSelected>>", atualizar_calendario)
        sp_ano.config(command=atualizar_calendario)

        # ===== GRADE FIXA DO CALENDÁRIO =====
        grid = ttk.Frame(self.frame_cal)
        grid.pack(pady=6)

        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, d in enumerate(dias):
            ttk.Label(grid, text=d, width=4, anchor="center").grid(row=0, column=i)

        cal = calendar.Calendar(calendar.SUNDAY)
        semanas = cal.monthdayscalendar(self.ano_atual, self.mes_atual)

        # Força sempre 6 semanas (altura fixa)
        while len(semanas) < 6:
            semanas.append([0] * 7)

        for r, semana in enumerate(semanas, start=1):
            for c, dia in enumerate(semana):
                texto = str(dia) if dia != 0 else ""
                ttk.Label(
                    grid,
                    text=texto,
                    width=4,
                    anchor="center"
                ).grid(row=r, column=c, padx=2, pady=2)

    # =================== CLIENTES (placeholder) ===================
    def atualizar_lista(self):
        pass


# =================== MAIN ===================
if __name__ == "__main__":
    root = tk.Tk()
    GestorApp(root)
    root.mainloop()

