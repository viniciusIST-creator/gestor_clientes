import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, date

ARQUIVO = "dados.json"


# =================== DADOS ===================
def carregar():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # MIGRAÇÃO AUTOMÁTICA (bool -> dict)
    for cliente, itens in dados.items():
        for nome, valor in list(itens.items()):
            if isinstance(valor, bool):
                itens[nome] = {"feito": valor, "data": None}
    return dados


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def str_para_data(s):
    return datetime.strptime(s, "%d/%m/%Y").date()


# =================== APP ===================
class GestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Me lembra se não eu esqueço – Vinicius")
        self.root.geometry("1200x560")
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        self.dados = carregar()
        self.cliente_atual = None
        self.check_vars = {}

        self.configurar_estilo()
        self.build_ui()
        self.atualizar_lista()

    # =================== ESTILO ===================
    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

    # =================== UI ===================
    def build_ui(self):
        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.middle = ttk.Frame(self.root, padding=10)
        self.middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH)

        # -------- CLIENTES --------
        ttk.Label(self.left, text="Clientes", style="Header.TLabel").pack(anchor="w")
        self.lista = tk.Listbox(self.left, width=30)
        self.lista.pack(fill=tk.Y, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente",
                   command=self.novo_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Editar Cliente",
                   command=self.editar_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Remover Cliente",
                   command=self.remover_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Importar JSON",
                   command=self.importar_json).pack(fill=tk.X, pady=6)

        # -------- ITENS --------
        self.lbl_cliente = ttk.Label(self.middle, text="Checklist",
                                     style="Header.TLabel")
        self.lbl_cliente.pack(anchor="w")

        self.frame_checks = ttk.Frame(self.middle)
        self.frame_checks.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self.middle, text="Adicionar Item",
                   command=self.adicionar_item).pack(side=tk.LEFT)
        ttk.Button(self.middle, text="Remover Item Marcado",
                   command=self.remover_item_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.middle, text="Salvar",
                   command=self.salvar_checklist).pack(side=tk.RIGHT)

        # -------- TAREFAS POR DATA --------
        ttk.Label(self.right, text="Tarefas por Data",
                  style="Header.TLabel").pack(anchor="w")

        self.tree = ttk.Treeview(
            self.right,
            columns=("cliente", "item", "data"),
            show="headings",
            height=20
        )
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("item", text="Item")
        self.tree.heading("data", text="Data")
        self.tree.pack(fill=tk.BOTH, expand=True)

    # =================== CLIENTES ===================
    def atualizar_lista(self):
        self.lista.delete(0, tk.END)
        for c in sorted(self.dados.keys()):
            self.lista.insert(tk.END, c)

    def novo_cliente(self):
        nome = simpledialog.askstring("Novo Cliente", "Nome:")
        if nome and nome not in self.dados:
            self.dados[nome] = {}
            salvar(self.dados)
            self.atualizar_lista()

    def editar_cliente(self):
        if not self.cliente_atual:
            return
        novo = simpledialog.askstring("Editar", "Novo nome:",
                                      initialvalue=self.cliente_atual)
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
            self.frame_checks.destroy()
            self.frame_checks = ttk.Frame(self.middle)
            self.frame_checks.pack(fill=tk.BOTH, expand=True)

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
            var = tk.BooleanVar(value=dados["feito"])
            texto = f"{item}  |  {dados['data'] or '—'}"
            ttk.Checkbutton(self.frame_checks,
                            text=texto,
                            variable=var).pack(anchor="w")
            self.check_vars[item] = var

    def adicionar_item(self):
        if not self.cliente_atual:
            return
        nome = simpledialog.askstring("Item", "Descrição:")
        if not nome:
            return

        data = simpledialog.askstring(
            "Data",
            "Data (dd/mm/aaaa) ou vazio:"
        )
        if data:
            try:
                str_para_data(data)
            except:
                messagebox.showerror("Erro", "Data inválida")
                return
        else:
            data = None

        self.dados[self.cliente_atual][nome] = {
            "feito": False,
            "data": data
        }
        salvar(self.dados)
        self.mostrar_checklist()
        self.atualizar_tarefas()

    def remover_item_selecionado(self):
        for item, var in self.check_vars.items():
            if var.get():
                del self.dados[self.cliente_atual][item]
                break
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
                d = str_para_data(dados["data"])
                if d < hoje:
                    tag = "vencida"
                elif d == hoje:
                    tag = "hoje"
                else:
                    tag = "proxima"
                self.tree.insert("", tk.END,
                                 values=(cliente, nome, dados["data"]),
                                 tags=(tag,))

        self.tree.tag_configure("vencida", background="#ffcccc")
        self.tree.tag_configure("hoje", background="#fff3cd")
        self.tree.tag_configure("proxima", background="#d4edda")

    # =================== OUTROS ===================
    def importar_json(self):
        caminho = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not caminho:
            return
        with open(caminho, "r", encoding="utf-8") as f:
            self.dados = json.load(f)
        salvar(self.dados)
        self.atualizar_lista()

    def ao_fechar(self):
        salvar(self.dados)
        self.root.destroy()


# =================== MAIN ===================
if __name__ == "__main__":
    root = tk.Tk()
    GestorApp(root)
    root.mainloop()

