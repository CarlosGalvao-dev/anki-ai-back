# -*- coding: utf-8 -*-
import html
import re

def clean_front_text(html_content: str) -> str:
    """
    Remove tags HTML e converte entidades para texto puro legível pelo Gemini.
    """
    if not html_content:
        return ""
    
    text = html_content
    # Substitui quebras de linha e divs por quebras de linha reais
    text = re.sub(r'<(?:br|div|p)\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Remove qualquer outra tag HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Decodifica entidades HTML (&nbsp;, &amp;, etc.)
    text = html.unescape(text)
    # Remove espaços repetidos e linhas vazias excessivas
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(line for line in lines if line).strip()

def clean_ai_output(ai_response: str) -> str:
    """
    Higieniza a resposta da IA: remove blocos markdown desnecessários e
    garante que o conteúdo seja renderizado perfeitamente no Anki.
    """
    if not ai_response:
        return ""

    text = ai_response.strip()

    # Remove blocos de código ```html ... ``` ou ``` ... ```
    if text.startswith("```"):
        text = re.sub(r'^```(?:html|HTML)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        text = text.strip()

    # Se a IA por algum motivo retornou Markdown puro (sem tags HTML),
    # converte negritos, itálicos e quebras de linha básicas para HTML
    if "<div" not in text.lower() and "<p" not in text.lower() and "<b" not in text.lower():
        # Converte **negrito** para <b>negrito</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Converte *itálico* para <i>itálico</i>
        text = re.sub(r'\*([^*]+?)\*', r'<i>\1</i>', text)
        # Converte quebras de linha normais para <br>
        text = text.replace('\n', '<br>')

    return text
