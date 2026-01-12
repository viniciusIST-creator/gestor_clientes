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
        self.root.title("Lembra Lembra dos clientes – Vinicius")
        self.root.geometry("950x520")
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        self.dados = carregar()
        self.cliente_atual = None
        self.check_vars = {}

        self.build_ui()
        self.atualizar_lista()

    # ---------- INTERFACE ----------
    def build_ui(self):
        style = ttk.Style()
        style.theme_use("default")

        self.left = ttk.Frame(self.root, padding=10)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = ttk.Frame(self.root, padding=10)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(self.left, text="Pesquisar cliente").pack(anchor="w")
        self.var_pesquisa = tk.StringVar()
        self.var_pesquisa.trace_add("write", lambda *_: self.atualizar_lista())
        ttk.Entry(self.left, textvariable=self.var_pesquisa).pack(fill=tk.X, pady=5)

        ttk.Label(self.left, text="Clientes", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.lista = tk.Listbox(self.left, width=32)
        self.lista.pack(fill=tk.Y, expand=True)
        self.lista.bind("<<ListboxSelect>>", self.selecionar_cliente)

        ttk.Button(self.left, text="Novo Cliente", command=self.novo_cliente).pack(fill=tk.X, pady=4)
        ttk.Button(self.left, text="Editar Cliente", command=self.editar_cliente).pack(fill=tk.X, pady=4)
        ttk.Button(self.left, text="Remover Cliente", command=self.remover_cliente).pack(fill=tk.X, pady=4)

        self.lbl_cliente = ttk.Label(
            self.right,
            text="Selecione um cliente",
            font=("Segoe UI", 11, "bold")
        )
        self.lbl_cliente.pack(anchor="w")

        self.frame_checks = ttk.Frame(self.right)
        self.frame_checks.pack(fill=tk.BOTH, expand=True, pady=10)

        btns = ttk.Frame(self.right)
        btns.pack(fill=tk.X)

        ttk.Button(btns, text="Adicionar Item", comman
