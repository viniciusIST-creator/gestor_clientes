import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

ARQUIVO = "dados.json"


def carregar():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


class GestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Clientes e Ensaios – Vinicius Coelho")
        self.root.geometry("900x500")

        self.dados = carregar()
        self.cliente_atual = None
        self.check_vars = {}

        self.build_ui()
        self.atualizar_lista()

    def build_ui(self):
        style = ttk.Style()
        style.theme_use("default")

        # Layout principal
        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Pesquisa
        ttk.Label(self.left, text="Pesquisar cliente").pack(anchor="w")
        self.var_pesquisa = tk.StringVar()
        self.var_pesquisa.trace_add("write", lambda *_: self.atualizar_lista())
        ttk.Entry(self.left, textvariable=self.var_pesquisa).pack(fill=tk.X, pady=5)

        # Lista clientes
        ttk.Label(self.left, text="Clientes", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.lista = tk.Listbox(self.left, width=30)
        self.lista.pack(fill=tk.Y, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente", command=self.novo_cliente).pack(fill=tk.X, pady=5)

        # Checklist
        self.lbl_cliente = ttk.Label(self.right, text="Selecione um cliente",
                                     font=("Segoe UI", 11, "bold"))
        self.lbl_cliente.pack(anchor="w")

        self.frame_checks = ttk.Frame(self.right)
        self.frame_checks.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botões
        btns = ttk.Frame(self.right)
        btns.pack(fill=tk.X)

        ttk.Button(btns, text="Adicionar Item", command=self.adicionar_item).pack(side=tk.LEFT)
        ttk.Button(btns, text="Remover Item Selecionado",
                   command=self.remover_item_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Salvar", command=self.salvar_checklist).pack(side=tk.RIGHT)

    def atualizar_lista(self):
        termo = self.var_pesquisa.get().lower()
        self.lista.delete(0, tk.END)
        for cliente in self.dados:
            if termo in cliente.lower():
                self.lista.insert(tk.END, cliente)

    def novo_cliente(self):
        nome = simpledialog.askstring("Novo Cliente", "Nome do cliente:")
        if not nome:
            return
        if nome in self.dados:
            messagebox.showerror("Erro", "Cliente já existe.")
            return
        self.dados[nome] = {}
        salvar(self.dados)
        self.atualizar_lista()

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
            chk = ttk.Checkbutton(self.frame_checks, text=item, variable=var)
            chk.pack(anchor="w")
            self.check_vars[item] = var

    def adicionar_item(self):
        if not self.cliente_atual:
            return
        item = simpledialog.askstring("Adicionar Item", "Descrição do item:")
        if not item:
            return
        self.dados[self.cliente_atual][item] = False
        salvar(self.dados)
        self.mostrar_checklist()

    def remover_item_selecionado(self):
        if not self.cliente_atual:
            return

        selecionados = [
            item for item, var in self.check_vars.items() if var.get()
        ]

        if not selecionados:
            messagebox.showwarning("Aviso", "Marque o item que deseja remover.")
            return

        item = selecionados[0]

        if messagebox.askyesno("Confirmar", f"Remover '{item}'?"):
            del self.dados[self.cliente_atual][item]
            salvar(self.dados)
            self.mostrar_checklist()

    def salvar_checklist(self):
        if not self.cliente_atual:
            return
        for item, var in self.check_vars.items():
            self.dados[self.cliente_atual][item] = var.get()
        salvar(self.dados)
        messagebox.showinfo("Salvo", "Checklist salvo com sucesso.")


if __name__ == "__main__":
    root = tk.Tk()
    GestorApp(root)
    root.mainloop()
