import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

ARQUIVO_DADOS = "dados.json"


def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {}
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Clientes e Ensaios")

        self.dados = carregar_dados()
        self.cliente_atual = None
        self.check_vars = {}

        self.montar_interface()
        self.atualizar_lista_clientes()

    def montar_interface(self):
        frame_esq = tk.Frame(self.root, padx=10, pady=10)
        frame_esq.pack(side=tk.LEFT, fill=tk.Y)

        frame_dir = tk.Frame(self.root, padx=10, pady=10)
        frame_dir.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(frame_esq, text="Clientes").pack()
        self.lista_clientes = tk.Listbox(frame_esq, width=30)
        self.lista_clientes.pack()
        self.lista_clientes.bind("<<ListboxSelect>>", self.selecionar_cliente)

        tk.Button(frame_esq, text="Novo Cliente", command=self.novo_cliente).pack(pady=5)

        self.frame_checklist = frame_dir
        self.lbl_cliente = tk.Label(frame_dir, text="Selecione um cliente", font=("Arial", 12, "bold"))
        self.lbl_cliente.pack(anchor="w")

        self.checklist_container = tk.Frame(frame_dir)
        self.checklist_container.pack(anchor="w")

        tk.Button(frame_dir, text="Adicionar Item", command=self.adicionar_item).pack(pady=5)
        tk.Button(frame_dir, text="Salvar", command=self.salvar).pack(pady=5)
        tk.Button(frame_dir, text="Limpar Checklist", command=self.limpar_checklist).pack(pady=5)

    def atualizar_lista_clientes(self):
        self.lista_clientes.delete(0, tk.END)
        for cliente in self.dados:
            self.lista_clientes.insert(tk.END, cliente)

    def novo_cliente(self):
        nome = simpledialog.askstring("Novo Cliente", "Nome do cliente:")
        if not nome:
            return
        if nome in self.dados:
            messagebox.showerror("Erro", "Cliente já existe.")
            return
        self.dados[nome] = {}
        salvar_dados(self.dados)
        self.atualizar_lista_clientes()

    def selecionar_cliente(self, event):
        if not self.lista_clientes.curselection():
            return
        nome = self.lista_clientes.get(self.lista_clientes.curselection())
        self.cliente_atual = nome
        self.lbl_cliente.config(text=f"Checklist - {nome}")
        self.mostrar_checklist()

    def mostrar_checklist(self):
        for widget in self.checklist_container.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        checklist = self.dados.get(self.cliente_atual, {})
        for item, status in checklist.items():
            var = tk.BooleanVar(value=status)
            chk = tk.Checkbutton(self.checklist_container, text=item, variable=var)
            chk.pack(anchor="w")
            self.check_vars[item] = var

    def adicionar_item(self):
        if not self.cliente_atual:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return
        item = simpledialog.askstring("Novo Item", "Descrição do item:")
        if not item:
            return
        self.dados[self.cliente_atual][item] = False
        salvar_dados(self.dados)
        self.mostrar_checklist()

    def salvar(self):
        if not self.cliente_atual:
            return
        for item, var in self.check_vars.items():
            self.dados[self.cliente_atual][item] = var.get()
        salvar_dados(self.dados)
        messagebox.showinfo("Salvo", "Checklist salvo com sucesso.")

    def limpar_checklist(self):
        if not self.cliente_atual:
            return
        if messagebox.askyesno("Confirmar", "Remover todos os itens do checklist?"):
            self.dados[self.cliente_atual] = {}
            salvar_dados(self.dados)
            self.mostrar_checklist()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
