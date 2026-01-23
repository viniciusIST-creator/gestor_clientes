import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

ARQUIVO = "dados.json"


# =================== DADOS ===================
def carregar():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def validar_json(dados):
    if not isinstance(dados, dict):
        return False
    for cliente, checklist in dados.items():
        if not isinstance(cliente, str) or not isinstance(checklist, dict):
            return False
        for item, status in checklist.items():
            if not isinstance(item, str) or not isinstance(status, bool):
                return False
    return True


# =================== APP ===================
class GestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Me lembra se não eu esqueço – Vinicius")
        self.root.geometry("980x540")
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
        style.theme_use("clam")  # melhor tema nativo

        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 9), padding=6)
        style.configure("TCheckbutton", font=("Segoe UI", 10))

    # =================== UI ===================
    def build_ui(self):
        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(self.left, text="Pesquisar cliente").pack(anchor="w")
        self.var_pesquisa = tk.StringVar()
        self.var_pesquisa.trace_add("write", lambda *_: self.atualizar_lista())
        ttk.Entry(self.left, textvariable=self.var_pesquisa).pack(fill=tk.X, pady=5)

        ttk.Label(self.left, text="Clientes", style="Header.TLabel").pack(anchor="w")
        self.lista = tk.Listbox(self.left, width=32, relief=tk.FLAT)
        self.lista.pack(fill=tk.Y, expand=True, pady=5)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente",
                   command=self.novo_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Editar Cliente",
                   command=self.editar_cliente).pack(fill=tk.X, pady=2)
        ttk.Button(self.left, text="Remover Cliente",
                   command=self.remover_cliente).pack(fill=tk.X, pady=2)

        ttk.Separator(self.left).pack(fill=tk.X, pady=8)
        ttk.Button(self.left, text="Importar JSON",
                   command=self.importar_json).pack(fill=tk.X)

        self.lbl_cliente = ttk.Label(
            self.right,
            text="Selecione um cliente",
            style="Header.TLabel"
        )
        self.lbl_cliente.pack(anchor="w")

        # --------- CHECKLIST COM SCROLL ---------
        self.canvas = tk.Canvas(self.right, highlightthickness=0)
        self.scroll = ttk.Scrollbar(self.right, orient=tk.VERTICAL,
                                    command=self.canvas.yview)
        self.frame_checks = ttk.Frame(self.canvas)

        self.frame_checks.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0),
                                  window=self.frame_checks,
                                  anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        btns = ttk.Frame(self.right)
        btns.pack(fill=tk.X)

        ttk.Button(btns, text="Adicionar Item",
                   command=self.adicionar_item).pack(side=tk.LEFT)
        ttk.Button(btns, text="Remover Item Marcado",
                   command=self.remover_item_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Limpar Marcações",
                   command=self.limpar_marcacoes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Salvar",
                   command=self.salvar_checklist).pack(side=tk.RIGHT)

    # =================== CLIENTES ===================
    def atualizar_lista(self):
        termo = self.var_pesquisa.get().lower()
        self.lista.delete(0, tk.END)
        for cliente in sorted(self.dados.keys(), key=str.lower):
            if termo in cliente.lower():
                self.lista.insert(tk.END, cliente)

    def novo_cliente(self):
        nome = simpledialog.askstring("Novo Cliente", "Nome do cliente:")
        if not nome or nome in self.dados:
            return
        self.dados[nome] = {}
        salvar(self.dados)
        self.atualizar_lista()

    def editar_cliente(self):
        if not self.cliente_atual:
            return
        novo = simpledialog.askstring(
            "Editar Cliente",
            "Novo nome:",
            initialvalue=self.cliente_atual
        )
        if not novo or novo in self.dados:
            return
        self.dados[novo] = self.dados.pop(self.cliente_atual)
        self.cliente_atual = novo
        salvar(self.dados)
        self.atualizar_lista()
        self.lbl_cliente.config(text=f"Checklist – {novo}")

    def remover_cliente(self):
        if not self.cliente_atual:
            return
        if messagebox.askyesno("Confirmar",
                               f"Remover '{self.cliente_atual}'?"):
            del self.dados[self.cliente_atual]
            self.cliente_atual = None
            salvar(self.dados)
            self.atualizar_lista()
            self.lbl_cliente.config(text="Selecione um cliente")
            for w in self.frame_checks.winfo_children():
                w.destroy()

    # =================== IMPORTAÇÃO ===================
    def importar_json(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Arquivos JSON", "*.json")]
        )
        if not caminho:
            return
        with open(caminho, "r", encoding="utf-8") as f:
            dados_importados = json.load(f)

        if not validar_json(dados_importados):
            messagebox.showerror("Erro", "JSON incompatível")
            return

        self.dados.update(dados_importados)
        salvar(self.dados)
        self.atualizar_lista()

    # =================== CHECKLIST ===================
    def selecionar_cliente(self, _):
        if not self.lista.curselection():
            return
        self.cliente_atual = self.lista.get(self.lista.curselection())
        self.lbl_cliente.config(text=f"Checklist – {self.cliente_atual}")
        self.mostrar_checklist()

    def mostrar_checklist(self):
        for w in self.frame_checks.winfo_children():
            w.destroy()
        self.check_vars.clear()

        for item, status in self.dados[self.cliente_atual].items():
            var = tk.BooleanVar(value=status)
            ttk.Checkbutton(self.frame_checks,
                            text=item,
                            variable=var).pack(anchor="w", pady=2)
            self.check_vars[item] = var

    def adicionar_item(self):
        if not self.cliente_atual:
            return
        item = simpledialog.askstring("Adicionar Item", "Descrição:")
        if not item:
            return
        self.dados[self.cliente_atual][item] = False
        salvar(self.dados)
        self.mostrar_checklist()

    def remover_item_selecionado(self):
        selecionados = [i for i, v in self.check_vars.items() if v.get()]
        if not selecionados:
            messagebox.showwarning("Aviso", "Marque um item")
            return
        del self.dados[self.cliente_atual][selecionados[0]]
        salvar(self.dados)
        self.mostrar_checklist()

    def limpar_marcacoes(self):
        for item in self.dados[self.cliente_atual]:
            self.dados[self.cliente_atual][item] = False
        salvar(self.dados)
        self.mostrar_checklist()

    def salvar_checklist(self):
        for item, var in self.check_vars.items():
            self.dados[self.cliente_atual][item] = var.get()
        salvar(self.dados)

    def ao_fechar(self):
        salvar(self.dados)
        self.root.destroy()


# =================== MAIN ===================
if __name__ == "__main__":
    root = tk.Tk()
    GestorApp(root)
    root.mainloop()

