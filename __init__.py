# -*- coding: utf-8 -*-
"""
Gemini AI English Assistant for Anki
Gera automaticamente o verso de cards de inglês usando a API do Google Gemini.
"""

from aqt import mw
from aqt.qt import QAction

from .ui.config_dialog import open_config_dialog
from .ui.editor_action import init_editor_integration

def init_addon():
    if not mw:
        return

    # 1. Adiciona item no menu Ferramentas (Tools) da tela principal
    action = QAction("🤖 Configurações do Gemini AI...", mw)
    action.triggered.connect(lambda: open_config_dialog(mw))
    mw.form.menuTools.addAction(action)

    # 2. Registra o diálogo de configurações no gerenciador de Add-ons do Anki
    mw.addonManager.setConfigAction(__name__, open_config_dialog)

    # 3. Inicializa integração com o Editor de Notas (Adicionar / Editar)
    init_editor_integration()

init_addon()
