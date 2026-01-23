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


def date_para_str(d):
    return d.strftime("%d/%m/%y")


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
        self.root.title("Me lembra se não eu esqueço – Vinicius")
        self.root.geometry("1400x650")
        self.root.configure(bg="#2b2b2b")

        self.dados = carregar()
        self.cliente_atual = None
        self.check_vars = {}
        self.filtro_atual = "Todas"

        self.configurar_estilo()
        self.build_ui()
        self.atualizar_lista()

    # =================== ESTILO ===================
    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background="#2b2b2b", foreground="white")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", padding=6)
        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="white",
                        fieldbackground="#1e1e1e")
        style.map("Treeview",
                  background=[("selected", "#007acc")])

    # =================== UI ===================
    def build_ui(self):
        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.middle = ttk.Frame(self.root, padding=10)
        self.middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH)

        # ---------- CLIENTES ----------
        ttk.Label(self.left, text="Clientes", style="Header.TLabel").pack(anchor="w")
        self.lista = tk.Listbox(self.left, width=30, bg="#1e1e1e",
                                fg="white", selectbackground="#007acc")
        self.lista.pack(fill=tk.Y, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente", command=self.novo_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Editar Cliente", command=self.editar_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Remover Cliente", command=self.remover_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Importar JSON", command=self.importar_json).pack(fill=tk.X, pady=6)

        # ---------- TABELA 2 ----------
        self.lbl_cliente = ttk.Label(self.middle, text="Checklist", style="Header.TLabel")
        self.lbl_cliente.pack(anchor="w")

        self.frame_checks = ttk.Frame(self.middle)
        self.frame_checks.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self.middle, text="Adicionar Item", command=self.adicionar_item).pack(side=tk.LEFT)
        ttk.Button(self.middle, text="Salvar", command=self.salvar_checklist).pack(side=tk.RIGHT)

        # ---------- TABELA 3 ----------
        ttk.Label(self.right, text="Tarefas por Data", style="Header.TLabel").pack(anchor="w")

        self.combo_filtro = ttk.Combobox(
            self.right,
            values=["Todas", "Atrasadas", "Hoje", "Futuras"],
            state="readonly"
        )
        self.combo_filtro.set("Todas")
        self.combo_filtro.pack(fill=tk.X, pady=4)
        self.combo_filtro.bind("<<ComboboxSelected>>", self.aplicar_filtro)

        self.tree = ttk.Treeview(
            self.right,
            columns=("cliente", "item", "data"),
            show="headings",
            height=12
        )
        for c in ("cliente", "item", "data"):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.frame_cal = ttk.Frame(self.right)
        self.frame_cal.pack(fill=tk.X, pady=6)
        self.mostrar_calendario()

    # =================== CLIENTES ===================
    def atualizar_lista(self):
        self.lista.delete(0, tk.END)
        for c in sorted(self.dados.keys()):
            self.lista.insert(tk.END, c)

    def novo_cliente(self):
        nome = self.janela_texto("Novo Cliente", "")
        if nome:
            self.dados[nome] = {}
            salvar(self.dados)
            self.atualizar_lista()

    def editar_cliente(self):
        if not self.cliente_atual:
            return
        novo = self.janela_texto("Editar Cliente", self.cliente_atual)
        if novo:
            self.dados[novo] = self.dados.pop(self.cliente_atual)
            self.cliente_atual = novo
            salvar(self.dados)
            self.atualizar_lista()

    def remover_cliente(self):
        if self.cliente_atual and messagebox.askyesno("Confirmar", "Remover cliente?"):
            del self.dados[self.cliente_atual]
            self.cliente_atual = None
            salvar(self.dados)
            self.atualizar_lista()

    # =================== CHECKLIST ===================
    def selecionar_cliente(self, _):
        if not self.lista.curselection():
            return
        self.cliente_atual = self.lista.get(self.lista.curselection())
        self.lbl_cliente.config(text=f"Checklist – {self.cliente_atual}")
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def mostrar_checklist(self):
        for w in self.frame_checks.winfo_children():
            w.destroy()
        self.check_vars.clear()

        for item, dados in self.dados[self.cliente_atual].items():
            linha = ttk.Frame(self.frame_checks)
            linha.pack(fill=tk.X, pady=2)

            var = tk.BooleanVar(value=dados["feito"])
            chk = ttk.Checkbutton(linha, variable=var)
            chk.pack(side=tk.LEFT)

            ttk.Label(linha, text=item, width=50, anchor="w").pack(side=tk.LEFT)
            ttk.Label(linha, text=dados["data"] or "—", width=10).pack(side=tk.LEFT)

            ttk.Button(linha, text="Editar",
                       command=lambda i=item: self.editar_item(i)).pack(side=tk.LEFT)

            self.check_vars[item] = var

    def adicionar_item(self):
        nome = self.janela_texto("Novo Item", "")
        if not nome:
            return
        data = self.janela_texto("Data (dd/mm/aa)", "")
        if data:
            try:
                data_str_para_date(data)
            except:
                messagebox.showerror("Erro", "Data inválida")
                return
        else:
            data = None

        self.dados[self.cliente_atual][nome] = {"feito": False, "data": data}
        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def editar_item(self, item):
        dados = self.dados[self.cliente_atual][item]
        novo_nome = self.janela_texto("Editar Item", item)
        nova_data = self.janela_texto("Editar Data (dd/mm/aa)", dados["data"] or "")

        if nova_data:
            data_str_para_date(nova_data)
        else:
            nova_data = None

        self.dados[self.cliente_atual].pop(item)
        self.dados[self.cliente_atual][novo_nome] = {
            "feito": dados["feito"],
            "data": nova_data
        }
        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def salvar_checklist(self):
        for item, var in self.check_vars.items():
            self.dados[self.cliente_atual][item]["feito"] = var.get()
        salvar(self.dados)
        self.atualizar_tarefas()

    # =================== TAREFAS ===================
    def aplicar_filtro(self, _):
        self.filtro_atual = self.combo_filtro.get()
        self.atualizar_tarefas()

    def atualizar_tarefas(self):
        self.tree.delete(*self.tree.get_children())
        hoje = date.today()

        for cliente, itens in self.dados.items():
            for nome, dados in itens.items():
                if dados["feito"] or not dados["data"]:
                    continue
                d = data_str_para_date(dados["data"])

                status = "Futuras"
                if d < hoje:
                    status = "Atrasadas"
                elif d == hoje:
                    status = "Hoje"

                if self.filtro_atual != "Todas" and status != self.filtro_atual:
                    continue

                self.tree.insert("", tk.END,
                                 values=(cliente, nome, dados["data"]))

    # =================== CALENDÁRIO ===================
    def mostrar_calendario(self):
        for w in self.frame_cal.winfo_children():
            w.destroy()

        cal = calendar.Calendar(calendar.SUNDAY)
        hoje = date.today()

        ttk.Label(self.frame_cal, text=hoje.strftime("%B %Y"),
                  style="Header.TLabel").pack()

        grid = ttk.Frame(self.frame_cal)
        grid.pack()

        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, d in enumerate(dias):
            ttk.Label(grid, text=d).grid(row=0, column=i)

        for r, semana in enumerate(cal.monthdayscalendar(hoje.year, hoje.month), start=1):
            for c, dia in enumerate(semana):
                texto = str(dia) if dia else ""
                ttk.Label(grid, text=texto).grid(row=r, column=c, padx=4)

    # =================== JANELA TEXTO ===================
    def janela_texto(self, titulo, valor):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.geometry("500x250")

        txt = tk.Text(top, wrap="word")
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", valor)

        retorno = []

        def salvar_texto():
            retorno.append(txt.get("1.0", "end").strip())
            top.destroy()

        ttk.Button(top, text="OK", command=salvar_texto).pack(pady=4)
        self.root.wait_window(top)
        return retorno[0] if retorno else None

    # =================== OUTROS ===================
    def importar_json(self):
        caminho = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not caminho:
            return
        with open(caminho, "r", encoding="utf-8") as f:
            self.dados = json.load(f)
        salvar(self.dados)
        self.atualizar_lista()

# =================== MAIN ===================
if __name__ == "__main__":
    root = tk.Tk()
    GestorApp(root)
    root.mainloop()

