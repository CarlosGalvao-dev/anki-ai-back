# -*- coding: utf-8 -*-
try:
    from aqt.qt import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
        QComboBox, QCheckBox, QPlainTextEdit, QGroupBox, QTabWidget, QWidget,
        Qt, QRadioButton
    )
    from aqt.utils import showInfo, showWarning, tooltip
    from aqt import mw
except ImportError:
    # Para testes fora do Anki
    QDialog = object
    mw = None

from ..core import config_manager, ai_client

# Compatibilidade PyQt5 / PyQt6 para enums
ECHO_PASSWORD = getattr(QLineEdit.EchoMode, "Password", None) if hasattr(QLineEdit, "EchoMode") else getattr(QLineEdit, "Password", 2)
ECHO_NORMAL = getattr(QLineEdit.EchoMode, "Normal", None) if hasattr(QLineEdit, "EchoMode") else getattr(QLineEdit, "Normal", 0)
ALIGN_LEFT = getattr(Qt.AlignmentFlag, "AlignLeft", None) if hasattr(Qt, "AlignmentFlag") else getattr(Qt, "AlignLeft", 1)

class GeminiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Gemini AI English Assistant")
        self.resize(620, 520)
        self.config = config_manager.load_config()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        tabs = QTabWidget(self)

        # Tab 1: API & Geral
        tab_general = QWidget()
        layout_general = QVBoxLayout(tab_general)

        # Grupo: Credenciais da API
        group_api = QGroupBox("Google Gemini API")
        layout_api = QVBoxLayout(group_api)

        layout_key = QHBoxLayout()
        lbl_key = QLabel("API Key:")
        self.input_key = QLineEdit()
        self.input_key.setEchoMode(ECHO_PASSWORD)
        self.input_key.setText(self.config.get("api_key", ""))
        self.input_key.setPlaceholderText("Cole sua chave de API do Google AI Studio aqui...")

        self.btn_show_key = QCheckBox("Mostrar")
        self.btn_show_key.toggled.connect(self._toggle_key_visibility)

        layout_key.addWidget(lbl_key)
        layout_key.addWidget(self.input_key)
        layout_key.addWidget(self.btn_show_key)
        layout_api.addLayout(layout_key)

        # Modelo e Teste de Conexão
        layout_model = QHBoxLayout()
        lbl_model = QLabel("Modelo:")
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True)
        models = [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        self.combo_model.addItems(models)
        current_model = self.config.get("model", "gemini-2.0-flash")
        index = self.combo_model.findText(current_model)
        if index >= 0:
            self.combo_model.setCurrentIndex(index)
        else:
            self.combo_model.setEditText(current_model)

        self.btn_test = QPushButton("⚡ Testar Chave de API")
        self.btn_test.clicked.connect(self._test_api)

        layout_model.addWidget(lbl_model)
        layout_model.addWidget(self.combo_model, stretch=1)
        layout_model.addWidget(self.btn_test)
        layout_api.addLayout(layout_model)

        help_api_lbl = QLabel(
            "<small style='color: #666;'>Obtenha sua chave gratuitamente em: "
            "<a href='https://aistudio.google.com/app/apikey'>Google AI Studio</a></small>"
        )
        help_api_lbl.setOpenExternalLinks(True)
        layout_api.addWidget(help_api_lbl)
        layout_general.addWidget(group_api)

        # Grupo: Mapeamento de Campos e Comportamento
        group_fields = QGroupBox("Mapeamento dos Campos no Card")
        layout_fields = QVBoxLayout(group_fields)

        layout_f_names = QHBoxLayout()
        lbl_src = QLabel("Campo Origem (Inglês):")
        self.input_src = QLineEdit(self.config.get("source_field", "Front"))
        self.input_src.setPlaceholderText("Ex: Front, Frente...")

        lbl_tgt = QLabel("Campo Destino (Resultado):")
        self.input_tgt = QLineEdit(self.config.get("target_field", "Back"))
        self.input_tgt.setPlaceholderText("Ex: Back, Verso...")

        layout_f_names.addWidget(lbl_src)
        layout_f_names.addWidget(self.input_src)
        layout_f_names.addWidget(lbl_tgt)
        layout_f_names.addWidget(self.input_tgt)
        layout_fields.addLayout(layout_f_names)

        # Modo de inserção (Sobrescrever ou Adicionar)
        layout_mode = QHBoxLayout()
        lbl_mode = QLabel("Modo de inserção:")
        self.radio_overwrite = QRadioButton("Substituir conteúdo existente")
        self.radio_append = QRadioButton("Adicionar ao final (Append)")
        if self.config.get("append", False):
            self.radio_append.setChecked(True)
        else:
            self.radio_overwrite.setChecked(True)

        layout_mode.addWidget(lbl_mode)
        layout_mode.addWidget(self.radio_overwrite)
        layout_mode.addWidget(self.radio_append)
        layout_mode.addStretch(1)
        layout_fields.addLayout(layout_mode)

        # Atalho de teclado
        layout_shortcut = QHBoxLayout()
        lbl_shortcut = QLabel("Atalho no Editor:")
        self.input_shortcut = QLineEdit(self.config.get("shortcut", "Ctrl+Shift+G"))
        layout_shortcut.addWidget(lbl_shortcut)
        layout_shortcut.addWidget(self.input_shortcut)
        layout_shortcut.addStretch(1)
        layout_fields.addLayout(layout_shortcut)

        layout_general.addWidget(group_fields)
        layout_general.addStretch(1)
        tabs.addTab(tab_general, "⚙️ Geral & API")

        # Tab 2: Prompt da IA
        tab_prompt = QWidget()
        layout_prompt = QVBoxLayout(tab_prompt)

        lbl_prompt_desc = QLabel(
            "<b>Instruções do Sistema para o Gemini:</b><br>"
            "<small style='color: #666;'>Define a forma como a IA analisará o termo em inglês e gerará o verso do card.</small>"
        )
        layout_prompt.addWidget(lbl_prompt_desc)

        self.text_prompt = QPlainTextEdit()
        self.text_prompt.setPlainText(self.config.get("system_prompt", ""))
        layout_prompt.addWidget(self.text_prompt)

        btn_reset_prompt = QPushButton("🔄 Restaurar Prompt Padrão")
        btn_reset_prompt.clicked.connect(self._reset_prompt_default)
        layout_prompt.addWidget(btn_reset_prompt, alignment=ALIGN_LEFT)

        tabs.addTab(tab_prompt, "🤖 Prompt do Gemini")

        main_layout.addWidget(tabs)

        # Botões inferiores (Salvar / Cancelar)
        layout_actions = QHBoxLayout()
        layout_actions.addStretch(1)

        self.btn_save = QPushButton("💾 Salvar Configurações")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._save_and_close)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)

        layout_actions.addWidget(self.btn_cancel)
        layout_actions.addWidget(self.btn_save)
        main_layout.addLayout(layout_actions)

    def _toggle_key_visibility(self, checked: bool):
        if checked:
            self.input_key.setEchoMode(ECHO_NORMAL)
        else:
            self.input_key.setEchoMode(ECHO_PASSWORD)

    def _test_api(self):
        key = self.input_key.text().strip()
        model = self.combo_model.currentText().strip()
        if not key:
            showWarning("Por favor, digite ou cole sua API Key antes de testar.", parent=self)
            return

        self.btn_test.setEnabled(False)
        self.btn_test.setText("Testando conexão...")
        
        # Teste de conexão
        success, msg = ai_client.test_api_connection(key, model)
        
        self.btn_test.setEnabled(True)
        self.btn_test.setText("⚡ Testar Chave de API")

        if success:
            showInfo(msg, parent=self)
        else:
            showWarning(f"Falha no teste de conexão:\n\n{msg}", parent=self)

    def _reset_prompt_default(self):
        default_prompt = config_manager.DEFAULT_CONFIG.get("system_prompt", "")
        from ..core.config_manager import _get_local_config_path
        import json, os
        p = _get_local_config_path()
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_prompt = data.get("system_prompt", default_prompt)
            except Exception:
                pass
        self.text_prompt.setPlainText(default_prompt)
        tooltip("Prompt padrão restaurado!")

    def _save_and_close(self):
        self.config["api_key"] = self.input_key.text().strip()
        self.config["model"] = self.combo_model.currentText().strip()
        self.config["source_field"] = self.input_src.text().strip() or "Front"
        self.config["target_field"] = self.input_tgt.text().strip() or "Back"
        self.config["append"] = self.radio_append.isChecked()
        self.config["shortcut"] = self.input_shortcut.text().strip() or "Ctrl+Shift+G"
        self.config["system_prompt"] = self.text_prompt.toPlainText().strip()

        if config_manager.save_config(self.config):
            tooltip("Configurações do Gemini AI salvas com sucesso!")
            self.accept()
        else:
            showWarning("Não foi possível salvar as configurações.", parent=self)

def open_config_dialog(parent=None):
    dialog = GeminiConfigDialog(parent=parent or mw)
    dialog.exec()
