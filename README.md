# 🤖 Gemini AI English Assistant para Anki

Extensão para o **Anki** projetada para quem estuda inglês. Ela permite que você digite uma palavra ou frase no campo frontal (**Front/Frente**) e, com um único clique ou atalho de teclado (`Ctrl+Shift+G`), a IA do **Google Gemini** gera o verso (**Back/Verso**) formatado, pronto para memorização.

---

## 🚀 Funcionalidades
- **Geração Inteligente para Inglês**: Tradução contextual, pronúncia fonética (IPA), classe gramatical, explicação de uso e frases de exemplo com tradução em português.
- **Botão Dedicado no Editor**: Botão estilizado com ícone do Gemini adicionado à barra de ferramentas do editor de notas do Anki.
- **Atalho de Teclado**: Pressione `Ctrl + Shift + G` no editor para acionar a geração instantaneamente.
- **Totalmente Assíncrono (QueryOp)**: Não congela o Anki nem bloqueia sua digitação durante a requisição à IA.
- **Tela de Configurações no Menu Ferramentas**:
  - Inserção e teste de API Key com 1 clique.
  - Seleção de modelos (`gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-1.5-flash`, etc.).
  - Mapeamento flexível de campos (funciona com notas em português *Frente/Verso* ou inglês *Front/Back*).
  - Editor de prompt do sistema personalizável com botão de restauração.
  - Alternância entre sobrescrever ou anexar conteúdo.

---

## 🛠️ Como Obter a Chave da API (Gratuita)
1. Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Faça login com sua conta Google.
3. Clique em **"Create API key"** (Criar chave de API).
4. Copie a chave gerada.

---

## ⚙️ Configuração no Anki
1. Abra ou reinicie o Anki.
2. Na janela principal, vá ao menu superior:
   **`Ferramentas` > `🤖 Configurações do Gemini AI...`**
3. Cole sua chave no campo **API Key**.
4. Clique em **⚡ Testar Chave de API** para validar a conexão.
5. Clique em **Salvar Configurações**.

---

## 📖 Como Usar no Dia a Dia
1. No Anki, clique em **Adicionar** (ou edite um card existente).
2. No campo **Front** (ou Frente), digite uma palavra, phrasal verb ou frase em inglês (ex: `take for granted` ou `I ran out of coffee`).
3. Clique no botão **✨ Gemini** na barra de ferramentas do editor ou aperte **`Ctrl + Shift + G`**.
4. O campo **Back** (ou Verso) será preenchido automaticamente com a tradução, explicação, IPA e exemplos práticos!
