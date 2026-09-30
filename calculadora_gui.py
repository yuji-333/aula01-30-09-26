import ast
import math
import re
from pathlib import Path
import tkinter as tk


class Calculator:
    """Calculadora gráfica com avaliação segura de operações aritméticas."""

    COLORS = {
        "background": "#101010",
        "display": "#1a1919",
        "text": "#f5f0e8",
        "muted": "#b5aaa3",
        "number": "#252222",
        "utility": "#393333",
        "operator": "#76252b",
        "equals": "#e85d26",
        "equals_text": "#ffffff",
        "border": "#493b38",
    }
    ARRANCAR_NAMES = {
        "0": "YAMMY",
        "1": "STARRK",
        "2": "BARAGGAN",
        "3": "HARRIBEL",
        "4": "ULQUIORRA",
        "5": "NNOITRA",
        "6": "GRIMMJOW",
        "7": "ZOMMARI",
        "8": "SZAYEL",
        "9": "AARONIERO",
    }

    def __init__(self, root):
        self.root = root
        self.expression = ""
        self.just_calculated = False

        # Configura a janela principal e define o comportamento da grade.
        root.title("BLEACH | Calculadora")
        root.configure(bg=self.COLORS["background"])
        root.resizable(False, False)
        root.minsize(340, 500)

        container = tk.Frame(root, bg=self.COLORS["background"], padx=16, pady=16)
        container.grid(row=0, column=0, sticky="nsew")

        heading = tk.Label(
            container,
            text="BLEACH  /  SOUL SOCIETY",
            anchor="w",
            bg=self.COLORS["background"],
            fg=self.COLORS["text"],
            font=("Segoe UI", 13, "bold"),
        )
        heading.grid(row=0, column=0, columnspan=3, sticky="ew", padx=4, pady=(0, 10))
        division = tk.Label(
            container,
            text="13TH DIVISION",
            anchor="e",
            bg=self.COLORS["background"],
            fg=self.COLORS["equals"],
            font=("Segoe UI", 8, "bold"),
        )
        division.grid(row=0, column=3, sticky="ew", padx=4, pady=(0, 10))

        self.display = tk.StringVar(value="0")
        display = tk.Entry(
            container,
            textvariable=self.display,
            state="readonly",
            readonlybackground=self.COLORS["display"],
            disabledforeground=self.COLORS["text"],
            fg=self.COLORS["text"],
            insertwidth=0,
            justify="right",
            font=("Segoe UI", 30),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["border"],
        )
        display.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 12), ipady=18)

        # Os botões compartilham a mesma grade para manter dimensões regulares.
        self.arrancar_images = {}
        buttons = [
            ("C", 2, 0, "utility"), ("⌫", 2, 1, "utility"), ("%", 2, 2, "utility"), ("÷", 2, 3, "operator"),
            ("7", 3, 0, "number"), ("8", 3, 1, "number"), ("9", 3, 2, "number"), ("×", 3, 3, "operator"),
            ("4", 4, 0, "number"), ("5", 4, 1, "number"), ("6", 4, 2, "number"), ("−", 4, 3, "operator"),
            ("1", 5, 0, "number"), ("2", 5, 1, "number"), ("3", 5, 2, "number"), ("+", 5, 3, "operator"),
            ("^", 6, 0, "operator"), ("0", 6, 1, "number"), (".", 6, 2, "number"), ("=", 6, 3, "equals"),
        ]
        for label, row, column, kind in buttons:
            background = self.COLORS[kind]
            foreground = self.COLORS["equals_text"] if kind == "equals" else self.COLORS["text"]
            if kind == "number" and label in self.ARRANCAR_NAMES:
                key_frame = tk.Frame(container, bg=background, cursor="hand2")
                arrancar_image = self._load_arrancar_image(label)
                image_widgets = []
                digit_row = 0
                if arrancar_image is not None:
                    self.arrancar_images[label] = arrancar_image
                    image_label = tk.Label(
                        key_frame,
                        image=arrancar_image,
                        bg=background,
                        cursor="hand2",
                    )
                    image_label.grid(row=0, column=0, sticky="nsew", pady=(4, 0))
                    image_widgets.append(image_label)
                    digit_row = 1
                digit = tk.Label(
                    key_frame,
                    text=label,
                    bg=background,
                    fg=foreground,
                    font=("Segoe UI", 17, "bold"),
                    cursor="hand2",
                )
                digit.grid(row=digit_row, column=0, sticky="ew", pady=(4, 0))
                arrancar = tk.Label(
                    key_frame,
                    text=self.ARRANCAR_NAMES[label],
                    bg=background,
                    fg=self.COLORS["muted"],
                    font=("Segoe UI", 7, "bold"),
                    cursor="hand2",
                )
                arrancar.grid(row=digit_row + 1, column=0, sticky="ew", pady=(0, 5))
                key_frame.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
                for widget in (key_frame, digit, arrancar, *image_widgets):
                    widget.bind("<Button-1>", lambda event, value=label: self._press(value))
                continue

            button = tk.Button(
                container,
                text=label,
                command=lambda value=label: self._press(value),
                font=("Segoe UI", 17, "bold" if kind in ("operator", "equals") else "normal"),
                bg=background,
                fg=foreground,
                activebackground=background,
                activeforeground=foreground,
                relief="flat",
                bd=0,
                cursor="hand2",
                takefocus=False,
            )
            button.grid(row=row, column=column, sticky="nsew", padx=4, pady=4, ipadx=8, ipady=10)

        for column in range(4):
            container.grid_columnconfigure(column, weight=1, uniform="calculator_columns")
        for row in range(2, 7):
            container.grid_rowconfigure(row, weight=1, uniform="calculator_rows")

        # Recebe entrada do teclado, incluindo teclas do teclado numérico.
        root.bind("<Key>", self._on_key)
        root.focus_set()

    def _load_arrancar_image(self, digit):
        image_directory = Path(__file__).resolve().parent / "assets" / "arrancar"
        for extension in (".png", ".gif"):
            image_path = image_directory / f"{digit}{extension}"
            if not image_path.is_file():
                continue
            try:
                image = tk.PhotoImage(file=str(image_path))
            except tk.TclError:
                continue
            scale = max(1, math.ceil(max(image.width(), image.height()) / 38))
            return image.subsample(scale, scale)
        return None

    def _press(self, key):
        if key == "C":
            self._clear()
        elif key == "⌫":
            self._backspace()
        elif key == "=":
            self._calculate()
        elif key in ("+", "−", "×", "÷", "^"):
            self._append({"−": "-", "×": "*", "÷": "/"}.get(key, key), operator=True)
        else:
            self._append(key)

    def _append(self, value, operator=False):
        if self.display.get() == "Erro":
            self._clear()

        if self.just_calculated:
            if operator:
                self.expression = self.display.get()
            else:
                self.expression = ""
            self.just_calculated = False

        if operator:
            if not self.expression:
                if value != "-":
                    return
            elif self.expression[-1] in "+-*/^":
                if value == "-" and self.expression[-1] != "-":
                    self.expression += value
                else:
                    self.expression = self.expression[:-1] + value
                self._refresh_display()
                return
        elif value == ".":
            current_number = re.split(r"[+*/^()-]", self.expression)[-1]
            if "." in current_number:
                return
            if not current_number or current_number == "-":
                value = "0."

        self.expression += value
        self._refresh_display()

    def _refresh_display(self):
        self.display.set(self.expression or "0")

    def _clear(self):
        self.expression = ""
        self.just_calculated = False
        self.display.set("0")

    def _backspace(self):
        if self.display.get() == "Erro" or self.just_calculated:
            self._clear()
            return
        self.expression = self.expression[:-1]
        self._refresh_display()

    def _calculate(self):
        if not self.expression:
            return
        try:
            # % é um operador pós-fixado de porcentagem; ^ representa potência.
            normalized = re.sub(r"(?<=[0-9.)])%", "/100", self.expression)
            tree = ast.parse(normalized.replace("^", "**"), mode="eval")
            result = self._evaluate(tree.body)
            if not math.isfinite(result):
                raise ValueError("Resultado não finito")
            formatted = self._format_number(result)
        except (ArithmeticError, SyntaxError, ValueError, TypeError, OverflowError):
            self.expression = ""
            self.display.set("Erro")
            self.just_calculated = False
            return

        self.expression = formatted
        self.display.set(formatted)
        self.just_calculated = True

    def _evaluate(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow):
                if abs(right) > 1000:
                    raise ValueError("Expoente fora do limite")
                return left**right
        raise ValueError("Expressão inválida")

    @staticmethod
    def _format_number(value):
        if isinstance(value, int):
            return str(value)
        if value.is_integer():
            return str(int(value))
        return f"{value:.12g}"

    def _on_key(self, event):
        if event.keysym in ("Return", "KP_Enter") or event.char == "=":
            self._calculate()
        elif event.keysym == "BackSpace":
            self._backspace()
        elif event.keysym == "Escape":
            self._clear()
        elif event.char and event.char in "0123456789.+-*/^%()":
            self._append(event.char, operator=event.char in "+-*/^")
        elif event.char and event.char in "cC":
            self._clear()
        else:
            return
        return "break"


if __name__ == "__main__":
    window = tk.Tk()
    Calculator(window)
    window.mainloop()