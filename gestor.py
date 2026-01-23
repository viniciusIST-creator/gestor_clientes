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
        self.root.title("Me lembra se não eu esqueço – Vinicius")
        self.root.geometry("1400x650")
        self.root.configure(bg="white")

        self.dados = carregar()
        self.cliente_atual = None
        self.item_selecionado = None
        self.check_vars = {}
        self.filtro_atual = "Todas"

        self.configurar_estilo()
        self.build_ui()
        self.atualizar_lista()

    # =================== ESTILO ===================
    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
    
        azul = "#1f6aa5"
        azul_claro = "#cce0f5"
    
        # ===== Labels =====
        style.configure("TLabel", background="white", foreground="black")
        style.configure("Header.TLabel",
                        font=("Segoe UI", 12, "bold"),
                        foreground=azul,
                        background="white")
    
        # ===== Treeview =====
        style.configure("Treeview",
                        background="white",
                        fieldbackground="white",
                        foreground="black",
                        rowheight=26)
        style.map("Treeview",
                  background=[("selected", azul_claro)],
                  foreground=[("selected", "black")])
    
        # ===== Frame da checklist =====
        style.configure("TFrame", background="white")
        style.configure("Selected.TFrame", background=azul_claro)
    
        # ===== Botões =====
        style.configure("TButton",
                        padding=6,
                        background="white",
                        foreground="black")
        style.map("TButton",
                  background=[("active", "#e6f0fa")],
                  foreground=[("disabled", "#888")])

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

        self.lista = tk.Listbox(self.left, width=30, selectbackground="#cce0f5")
        self.lista.pack(fill=tk.Y, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente", command=self.novo_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Editar Cliente", command=self.editar_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Remover Cliente", command=self.remover_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Importar JSON", command=self.importar_json).pack(fill=tk.X, pady=6)

        # ---------- CHECKLIST ----------
        self.lbl_cliente = ttk.Label(self.middle, text="Checklist", style="Header.TLabel")
        self.lbl_cliente.pack(anchor="w")

        self.frame_checks = ttk.Frame(self.middle)
        self.frame_checks.pack(fill=tk.BOTH, expand=True)

        botoes = ttk.Frame(self.middle)
        botoes.pack(fill=tk.X, pady=6)

        ttk.Button(botoes, text="Adicionar Item", command=self.adicionar_item).pack(side=tk.LEFT)
        ttk.Button(botoes, text="Editar Tarefa", command=self.editar_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Apagar Item", command=self.apagar_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Limpar Checklist", command=self.limpar_checklist).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Salvar", command=self.salvar_checklist).pack(side=tk.RIGHT)

        # ---------- TAREFAS POR DATA ----------
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

        self.tree.tag_configure("atrasada", background="#ffd6d6")
        self.tree.tag_configure("hoje", background="#fff3cd")
        self.tree.tag_configure("futura", background="#d4edda")

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
        self.item_selecionado = None
        self.linhas_check = {}  # para poder destacar a linha selecionada
    
        for item, dados in self.dados[self.cliente_atual].items():
            linha = ttk.Frame(self.frame_checks)
            linha.pack(fill=tk.X, pady=2)
            self.linhas_check[item] = linha
    
            var = tk.BooleanVar(value=dados["feito"])
            chk = ttk.Checkbutton(linha, variable=var)
            chk.pack(side=tk.LEFT)
    
            lbl = ttk.Label(linha, text=item, width=50, anchor="w")
            lbl.pack(side=tk.LEFT)
    
            ttk.Label(linha, text=dados["data"] or "—", width=10).pack(side=tk.LEFT)
    
            # Bind em toda a linha
            def selecionar(e, nome=item):
                # Desmarca destaque da linha anterior
                if self.item_selecionado and self.item_selecionado in self.linhas_check:
                    self.linhas_check[self.item_selecionado].configure(style="TFrame")
                self.item_selecionado = nome
                linha.configure(style="Selected.TFrame")  # estilo para destacar
    
            linha.bind("<Button-1>", selecionar)
            lbl.bind("<Button-1>", selecionar)
            chk.bind("<Button-1>", selecionar)  # clique no checkbox também seleciona
    
            self.check_vars[item] = var

    def selecionar_item(self, item):
        self.item_selecionado = item

    def adicionar_item(self):
        if not self.cliente_atual:
            return
        res = self.janela_tarefa("Nova Tarefa")
        if not res:
            return

        self.dados[self.cliente_atual][res["texto"]] = {"feito": False, "data": res["data"]}
        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def editar_item(self):
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa")
            return

        dados = self.dados[self.cliente_atual][self.item_selecionado]
        res = self.janela_tarefa("Editar Tarefa", self.item_selecionado, dados["data"] or "")
        if not res:
            return

        self.dados[self.cliente_atual].pop(self.item_selecionado)
        self.dados[self.cliente_atual][res["texto"]] = {"feito": dados["feito"], "data": res["data"]}
        self.item_selecionado = None

        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def apagar_item(self):
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa")
            return

        if messagebox.askyesno("Confirmar", "Apagar esta tarefa?"):
            self.dados[self.cliente_atual].pop(self.item_selecionado)
            self.item_selecionado = None
            salvar(self.dados)
            self.mostrar_checklist()
            self.atualizar_tarefas()

    def limpar_checklist(self):
        if not self.cliente_atual:
            return

        if messagebox.askyesno("Confirmar", "Remover TODAS as tarefas deste cliente?"):
            self.dados[self.cliente_atual] = {}
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

                if d < hoje:
                    tag = "atrasada"
                    status = "Atrasadas"
                elif d == hoje:
                    tag = "hoje"
                    status = "Hoje"
                else:
                    tag = "futura"
                    status = "Futuras"

                if self.filtro_atual != "Todas" and status != self.filtro_atual:
                    continue

                self.tree.insert("", tk.END,
                                 values=(cliente, nome, dados["data"]),
                                 tags=(tag,))

    # =================== CALENDÁRIO ===================
    def mostrar_calendario(self):
        for w in self.frame_cal.winfo_children():
            w.destroy()

        hoje = date.today()
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        ttk.Label(self.frame_cal,
                  text=f"{meses[hoje.month - 1]} {hoje.year}",
                  style="Header.TLabel").pack()

        cal = calendar.Calendar(calendar.SUNDAY)
        grid = ttk.Frame(self.frame_cal)
        grid.pack()

        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, d in enumerate(dias):
            ttk.Label(grid, text=d).grid(row=0, column=i)

        for r, semana in enumerate(cal.monthdayscalendar(hoje.year, hoje.month), start=1):
            for c, dia in enumerate(semana):
                ttk.Label(grid, text=str(dia) if dia else "").grid(row=r, column=c, padx=4)

    # =================== JANELAS ===================
    def janela_texto(self, titulo, valor):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.geometry("300x120")
        top.grab_set()

        frame = ttk.Frame(top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        entry = ttk.Entry(frame)
        entry.pack(fill=tk.X)
        entry.insert(0, valor)
        entry.focus()

        resultado = {}

        def confirmar(event=None):
            texto = entry.get().strip()
            if texto:
                resultado["valor"] = texto
                top.destroy()

        top.bind("<Return>", confirmar)
        ttk.Button(frame, text="OK", command=confirmar).pack(pady=8)

        self.root.wait_window(top)
        return resultado.get("valor")

    def janela_tarefa(self, titulo, desc="", data=""):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.geometry("360x150")
        top.resizable(False, False)
        top.grab_set()

        frame = ttk.Frame(top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Descrição:").pack(anchor="w")
        entry_desc = ttk.Entry(frame)
        entry_desc.pack(fill=tk.X)
        entry_desc.insert(0, desc)
        entry_desc.focus()

        ttk.Label(frame, text="Data (dd/mm/aa):").pack(anchor="w", pady=(6, 0))
        entry_data = ttk.Entry(frame)
        entry_data.pack(fill=tk.X)
        entry_data.insert(0, data)

        resultado = {}

        def confirmar(event=None):
            texto = entry_desc.get().strip()
            data_txt = entry_data.get().strip()

            if not texto:
                messagebox.showwarning("Aviso", "Descrição obrigatória")
                return

            if data_txt:
                try:
                    datetime.strptime(data_txt, "%d/%m/%y")
                except:
                    messagebox.showerror("Erro", "Data inválida (dd/mm/aa)")
                    return

            resultado["texto"] = texto
            resultado["data"] = data_txt or None
            top.destroy()

        top.bind("<Return>", confirmar)

        botoes = ttk.Frame(frame)
        botoes.pack(pady=8)

        ttk.Button(botoes, text="OK", command=confirmar).pack(side=tk.RIGHT)
        ttk.Button(botoes, text="Cancelar", command=top.destroy).pack(side=tk.RIGHT, padx=6)

        self.root.wait_window(top)
        return resultado if resultado else None

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

