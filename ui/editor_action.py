# -*- coding: utf-8 -*-
import os
import threading
from aqt import mw, gui_hooks
from aqt.utils import showWarning, tooltip

from ..core import config_manager, ai_client
from ..core.formatter import clean_front_text

def _run_async(parent_window, background_fn, on_success_fn, on_failure_fn, progress_label="Consultando Gemini AI..."):
    """
    Executa tarefas em segundo plano com máxima compatibilidade entre versões do Anki
    (Anki 2.1.20 até as versões mais recentes com aqt.operations.QueryOp).
    """
    # 1. Tenta aqt.operations.QueryOp (presente no Anki 2.1.50+)
    try:
        from aqt.operations import QueryOp
        op = QueryOp(
            parent=parent_window,
            op=lambda col: background_fn(),
            success=on_success_fn
        ).failure(on_failure_fn)
        if hasattr(op, "with_progress"):
            op.with_progress(progress_label)
        op.run_in_background()
        return
    except (ImportError, AttributeError):
        pass

    # 2. Fallback para mw.taskman.run_in_background (Anki 2.1.20+)
    try:
        if mw and hasattr(mw, "taskman") and hasattr(mw.taskman, "run_in_background"):
            def on_done(future):
                try:
                    res = future.result()
                    on_success_fn(res)
                except Exception as e:
                    on_failure_fn(e)
            mw.taskman.run_in_background(background_fn, on_done)
            return
    except Exception:
        pass

    # 3. Fallback universal usando threading + QTimer do Qt para retorno na thread principal
    from aqt.qt import QTimer
    def worker():
        try:
            res = background_fn()
            QTimer.singleShot(0, lambda: on_success_fn(res))
        except Exception as e:
            err = e
            QTimer.singleShot(0, lambda: on_failure_fn(err))

    threading.Thread(target=worker, daemon=True).start()

def _resolve_field_name(note, preferred_name: str, fallback_candidates: list[str], default_index: int) -> str:
    """
    Localiza o campo na nota. Se o nome configurado não existir,
    testa fallbacks comuns (ex: Frente/Front, Verso/Back) ou pega pelo índice.
    """
    fields = note.keys()
    if not fields:
        return ""
    
    # 1. Verifica se o preferido existe (case-insensitive)
    for f in fields:
        if f.lower() == preferred_name.lower():
            return f
            
    # 2. Testa lista de fallbacks
    for candidate in fallback_candidates:
        for f in fields:
            if f.lower() == candidate.lower():
                return f
                
    # 3. Usa pelo índice se válido
    if 0 <= default_index < len(fields):
        return fields[default_index]
        
    return fields[0]

def _run_gemini_generation(editor):
    note = editor.note
    if not note:
        return

    config = config_manager.load_config()
    api_key = config.get("api_key", "").strip()

    if not api_key:
        showWarning(
            "A Chave de API do Gemini ainda não foi configurada!\n\n"
            "Vá no menu 'Ferramentas > Configurações do Gemini AI...' para inserir sua chave.",
            parent=editor.parentWindow
        )
        return

    # Determina campo de origem
    src_field = _resolve_field_name(
        note, 
        config.get("source_field", "Front"), 
        ["Front", "Frente", "Inglês", "Expressão", "Palavra"], 
        0
    )

    # Determina campo de destino
    tgt_field = _resolve_field_name(
        note, 
        config.get("target_field", "Back"), 
        ["Back", "Verso", "Significado", "Tradução", "Resposta"], 
        1
    )

    raw_front = note[src_field]
    clean_text = clean_front_text(raw_front)

    if not clean_text:
        tooltip(f"O campo '{src_field}' está vazio! Digite um termo ou frase em inglês.", parent=editor.parentWindow)
        return

    model = config.get("model", "gemini-2.0-flash")
    system_prompt = config.get("system_prompt", "")
    append_mode = config.get("append", False)

    tooltip("Consultando o Gemini AI...", parent=editor.parentWindow)

    def background_task() -> str:
        return ai_client.generate_english_card(
            front_text=clean_text,
            api_key=api_key,
            system_prompt=system_prompt,
            model=model
        )

    def on_success(generated_html: str):
        if not generated_html:
            return

        if append_mode and note[tgt_field].strip():
            note[tgt_field] += "<br><hr style='border: none; border-top: 1px dashed #ccc;'><br>" + generated_html
        else:
            note[tgt_field] = generated_html

        # Recarrega o editor mantendo foco
        if hasattr(editor, "loadNoteKeepingFocus"):
            editor.loadNoteKeepingFocus()
        else:
            editor.loadNote()

        tooltip("✨ Conteúdo gerado com sucesso pelo Gemini!", parent=editor.parentWindow)

    def on_failure(exception: Exception):
        showWarning(
            f"Erro ao gerar conteúdo com Gemini:\n\n{str(exception)}",
            parent=editor.parentWindow
        )

    _run_async(
        parent_window=editor.parentWindow,
        background_fn=background_task,
        on_success_fn=on_success,
        on_failure_fn=on_failure,
        progress_label="O Gemini está elaborando a resposta..."
    )

def on_generate_button_clicked(editor):
    """Garante que qualquer digitação recente seja persistida na nota antes de processar."""
    if hasattr(editor, "saveNow"):
        editor.saveNow(lambda: _run_gemini_generation(editor))
    else:
        _run_gemini_generation(editor)

def add_gemini_editor_button(buttons: list, editor):
    config = config_manager.load_config()
    shortcut = config.get("shortcut", "Ctrl+Shift+G")

    # Caminho do ícone
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "assets", "gemini_icon.png")
    if not os.path.exists(icon_path):
        icon_path = None

    try:
        btn = editor.addButton(
            icon=icon_path,
            cmd="gemini_english_generate",
            func=lambda ed=editor: on_generate_button_clicked(ed),
            label="" if icon_path else "✨ Gemini",
            tip=f"Gerar card de Inglês com Gemini AI ({shortcut})",
            keys=shortcut,
            rightside=False
        )
    except TypeError:
        btn = editor.addButton(
            icon=icon_path,
            cmd="gemini_english_generate",
            func=lambda ed=editor: on_generate_button_clicked(ed),
            label="" if icon_path else "✨ Gemini",
            tip=f"Gerar card de Inglês com Gemini AI ({shortcut})",
            keys=shortcut
        )
    buttons.append(btn)

def init_editor_integration():
    gui_hooks.editor_did_init_buttons.append(add_gemini_editor_button)
