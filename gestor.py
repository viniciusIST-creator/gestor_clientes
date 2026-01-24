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
        return json.load(f)


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# =================== APP ===================
class GestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Me lembra se não eu esqueço – Vinicius")
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

        azul = "#1f6aa5"
        azul_claro = "#cce0f5"

        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black")
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=azul)

        style.configure("Treeview", rowheight=26)
        style.map("Treeview", background=[("selected", azul_claro)])

        style.configure("Selected.TFrame", background=azul_claro)

    # =================== UI ===================
    def build_ui(self):
        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.middle = ttk.Frame(self.root, padding=10)
        self.middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH)

        # CLIENTES
        ttk.Label(self.left, text="Clientes", style="Header.TLabel").pack(anchor="w")
        self.lista = tk.Listbox(self.left, width=30, selectbackground="#cce0f5")
        self.lista.pack(fill=tk.Y, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente", command=self.novo_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Editar Cliente", command=self.editar_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Remover Cliente", command=self.remover_cliente).pack(fill=tk.X, pady=2)

        # CHECKLIST
        self.lbl_cliente = ttk.Label(self.middle, text="Checklist", style="Header.TLabel")
        self.lbl_cliente.pack(anchor="w")

        self.frame_checks = ttk.Frame(self.middle)
        self.frame_checks.pack(fill=tk.BOTH, expand=True)

        botoes = ttk.Frame(self.middle)
        botoes.pack(fill=tk.X, pady=6)

        ttk.Button(botoes, text="Adicionar", command=self.adicionar_item).pack(side=tk.LEFT)
        ttk.Button(botoes, text="Editar", command=self.editar_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Apagar", command=self.apagar_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Salvar", command=self.salvar_checklist).pack(side=tk.RIGHT)

        # TAREFAS POR DATA
        ttk.Label(self.right, text="Tarefas por Data", style="Header.TLabel").pack(anchor="w")

        self.tree = ttk.Treeview(self.right, columns=("cliente", "item", "data"), show="headings")
        for c in ("cliente", "item", "data"):
            self.tree.heading(c, text=c.capitalize())
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.tag_configure("atrasada", background="#ffd6d6")
        self.tree.tag_configure("hoje", background="#fff3cd")
        self.tree.tag_configure("futura", background="#d4edda")

        # CALENDÁRIO
        self.frame_cal = ttk.Frame(self.right)
        self.frame_cal.pack(fill=tk.X, pady=8)
        self.mostrar_calendario()

    # =================== CLIENTES ===================
    def atualizar_lista(self):
        self.lista.delete(0, tk.END)
        for c in sorted(self.dados.keys()):
            self.lista.insert(tk.END, c)

    def selecionar_cliente(self, _):
        if not self.lista.curselection():
            return
        self.cliente_atual = self.lista.get(self.lista.curselection())
        self.lbl_cliente.config(text=f"Checklist – {self.cliente_atual}")
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def novo_cliente(self):
        nome = self.janela_texto("Novo Cliente")
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
    def mostrar_checklist(self):
        for w in self.frame_checks.winfo_children():
            w.destroy()
        self.check_vars.clear()
        self.item_selecionado = None

        for item, dados in self.dados[self.cliente_atual].items():
            linha = ttk.Frame(self.frame_checks)
            linha.pack(fill=tk.X, pady=2)

            var = tk.BooleanVar(value=dados["feito"])
            chk = ttk.Checkbutton(linha, variable=var)
            chk.pack(side=tk.LEFT)

            lbl = ttk.Label(linha, text=item, width=45)
            lbl.pack(side=tk.LEFT)

            ttk.Label(linha, text=dados["data"] or "—", width=10).pack(side=tk.LEFT)

            linha.bind("<Button-1>", lambda e, i=item: self.selecionar_item(i))
            lbl.bind("<Button-1>", lambda e, i=item: self.selecionar_item(i))
            chk.bind("<Button-1>", lambda e, i=item: self.selecionar_item(i))

            self.check_vars[item] = var

    def selecionar_item(self, item):
        self.item_selecionado = item

    def adicionar_item(self, data_pre=None):
        if not self.cliente_atual:
            return
        res = self.janela_tarefa("Nova Tarefa", data=data_pre)
        if not res:
            return
        self.dados[self.cliente_atual][res["texto"]] = {"feito": False, "data": res["data"]}
        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def editar_item(self):
        if not self.item_selecionado:
            return
        dados = self.dados[self.cliente_atual][self.item_selecionado]
        res = self.janela_tarefa("Editar Tarefa", self.item_selecionado, dados["data"])
        if not res:
            return
        self.dados[self.cliente_atual].pop(self.item_selecionado)
        self.dados[self.cliente_atual][res["texto"]] = {"feito": dados["feito"], "data": res["data"]}
        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def apagar_item(self):
        if self.item_selecionado:
            del self.dados[self.cliente_atual][self.item_selecionado]
            salvar(self.dados)
            self.mostrar_checklist()
            self.atualizar_tarefas()

    def salvar_checklist(self):
        for item, var in self.check_vars.items():
            self.dados[self.cliente_atual][item]["feito"] = var.get()
        salvar(self.dados)
        self.atualizar_tarefas()

    # =================== TAREFAS ===================
    def atualizar_tarefas(self):
        self.tree.delete(*self.tree.get_children())
        hoje = date.today()

        for cliente, itens in self.dados.items():
            for nome, dados in itens.items():
                if dados["feito"] or not dados["data"]:
                    continue
                d = data_str_para_date(dados["data"])
                tag = "futura"
                if d < hoje:
                    tag = "atrasada"
                elif d == hoje:
                    tag = "hoje"
                self.tree.insert("", tk.END, values=(cliente, nome, dados["data"]), tags=(tag,))

    # =================== CALENDÁRIO INTERATIVO ===================
    def mostrar_calendario(self):
        for w in self.frame_cal.winfo_children():
            w.destroy()

        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        topo = ttk.Frame(self.frame_cal)
        topo.pack()

        cb_mes = ttk.Combobox(topo, values=meses, state="readonly", width=12)
        cb_mes.current(self.mes_atual - 1)
        cb_mes.pack(side=tk.LEFT)

        sp_ano = tk.Spinbox(topo, from_=2000, to=2100, width=6)
        sp_ano.delete(0, tk.END)
        sp_ano.insert(0, self.ano_atual)
        sp_ano.pack(side=tk.LEFT, padx=6)

        def atualizar():
            self.mes_atual = cb_mes.current() + 1
            self.ano_atual = int(sp_ano.get())
            self.mostrar_calendario()

        cb_mes.bind("<<ComboboxSelected>>", lambda e: atualizar())
        sp_ano.config(command=atualizar)

        grid = ttk.Frame(self.frame_cal)
        grid.pack(pady=6)

        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, d in enumerate(dias):
            ttk.Label(grid, text=d, width=4).grid(row=0, column=i)

        cal = calendar.Calendar(calendar.SUNDAY)
        semanas = cal.monthdayscalendar(self.ano_atual, self.mes_atual)
        while len(semanas) < 6:
            semanas.append([0]*7)

        for r, semana in enumerate(semanas, start=1):
            for c, dia in enumerate(semana):
                if dia == 0:
                    ttk.Label(grid, text="", width=4).grid(row=r, column=c)
                else:
                    lbl = ttk.Label(grid, text=str(dia), width=4, anchor="center", relief="ridge")
                    lbl.grid(row=r, column=c, padx=1, pady=1)
                    lbl.bind("<Button-1>", lambda e, d=dia: self.adicionar_item(
                        date_para_str(date(self.ano_atual, self.mes_atual, d))
                    ))

    # =================== JANELAS ===================
    def janela_texto(self, titulo, valor=""):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.geometry("300x120")
        top.grab_set()

        entry = ttk.Entry(top)
        entry.pack(fill=tk.X, padx=10, pady=10)
        entry.insert(0, valor)
        entry.focus()

        res = {}

        def ok(event=None):
            res["v"] = entry.get()
            top.destroy()

        top.bind("<Return>", ok)
        ttk.Button(top, text="OK", command=ok).pack(pady=6)

        self.root.wait_window(top)
        return res.get("v")

    def janela_tarefa(self, titulo, texto="", data=""):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.geometry("360x160")
        top.grab_set()

        ttk.Label(top, text="Descrição").pack(anchor="w", padx=10)
        e_desc = ttk.Entry(top)
        e_desc.pack(fill=tk.X, padx=10)
        e_desc.insert(0, texto)

        ttk.Label(top, text="Data (dd/mm/aa)").pack(anchor="w", padx=10, pady=(6, 0))
        e_data = ttk.Entry(top)
        e_data.pack(fill=tk.X, padx=10)
        e_data.insert(0, data or "")

        res = {}

        def ok(event=None):
            if not e_desc.get():
                return
            res["texto"] = e_desc.get()
            res["data"] = e_data.get() or None
            top.destroy()

        top.bind("<Return>", ok)
        ttk.Button(top, text="OK", command=ok).pack(pady=8)

        self.root.wait_window(top)
        return res if res else None


# =================== MAIN ===================
if __name__ == "__main__":
    root = tk.Tk()
    GestorApp(root)
    root.mainloop()

