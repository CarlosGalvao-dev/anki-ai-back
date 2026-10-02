# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
import ssl
from .formatter import clean_ai_output

GEMINI_API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

class GeminiAPIError(Exception):
    pass

def generate_english_card(
    front_text: str,
    api_key: str,
    system_prompt: str,
    model: str = "gemini-2.0-flash",
    timeout: int = 25
) -> str:
    """
    Envia a frase ou palavra em inglês para o Google Gemini e retorna o HTML do verso.
    """
    if not api_key or not api_key.strip():
        raise GeminiAPIError("A chave de API (API Key) do Gemini não está configurada! Acesse 'Ferramentas > Configurações Gemini AI'.")

    if not front_text or not front_text.strip():
        raise GeminiAPIError("O campo de origem (Front) está vazio. Insira uma palavra ou frase em inglês.")

    url = GEMINI_API_URL_TEMPLATE.format(model=model.strip(), api_key=api_key.strip())

    # Monta o corpo da requisição
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"Termo / Frase em inglês a ser processada:\n{front_text.strip()}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }

    if system_prompt and system_prompt.strip():
        payload["systemInstruction"] = {
            "parts": [
                {"text": system_prompt.strip()}
            ]
        }

    json_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # Cria contexto SSL padrão
    context = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, data=json_data, timeout=timeout, context=context) as response:
            response_body = response.read().decode("utf-8")
            data = json.loads(response_body)

            candidates = data.get("candidates", [])
            if not candidates:
                raise GeminiAPIError("O Gemini não retornou nenhum candidato de resposta. A frase pode ter acionado filtros de segurança.")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise GeminiAPIError("Resposta vazia retornada pelo modelo Gemini.")

            raw_text = parts[0].get("text", "")
            return clean_ai_output(raw_text)

    except urllib.error.HTTPError as e:
        error_msg = f"Erro HTTP {e.code}"
        try:
            err_json = json.loads(e.read().decode("utf-8"))
            if "error" in err_json and "message" in err_json["error"]:
                gemini_msg = err_json["error"]["message"]
                if "API_KEY_INVALID" in gemini_msg or "API key not valid" in gemini_msg:
                    error_msg = "Chave de API inválida! Verifique a chave nas configurações do Gemini."
                elif "RESOURCE_EXHAUSTED" in gemini_msg or "quota" in gemini_msg.lower():
                    error_msg = "Limite de cota da API do Gemini excedido. Tente novamente em instantes."
                else:
                    error_msg = f"Erro da API Gemini ({e.code}): {gemini_msg}"
        except Exception:
            pass
        raise GeminiAPIError(error_msg)

    except urllib.error.URLError as e:
        raise GeminiAPIError(f"Erro de conexão com o Gemini: {e.reason}. Verifique sua conexão com a internet.")

    except Exception as e:
        raise GeminiAPIError(f"Falha inesperada ao contatar o Gemini: {str(e)}")

def test_api_connection(api_key: str, model: str = "gemini-2.0-flash") -> tuple[bool, str]:
    """
    Testa se a API Key e o modelo estão válidos com uma chamada simples.
    Retorna (sucesso: bool, mensagem: str).
    """
    try:
        res = generate_english_card(
            front_text="Hello world",
            api_key=api_key,
            system_prompt="Responda apenas com: OK",
            model=model,
            timeout=15
        )
        return True, "Conexão estabelecida com sucesso com o Google Gemini!"
    except GeminiAPIError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"
