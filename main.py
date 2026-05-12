name: Rodar Robô Diário
on:
  schedule:
    - cron: '0 11 * * *' # Roda todo dia às 08:00 (horário de Brasília é UTC-3)
  workflow_dispatch: # Permite rodar manualmente com um botão

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Instalar dependências
        run: |
          pip install -r requirements.txt
          playwright install chromium
      - name: Executar Robô
        run: python main.py
