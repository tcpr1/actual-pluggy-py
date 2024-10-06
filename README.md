# Actual-Pluggy-py

Brazilian Bank Sync for Actual with Pluggy using Python

# Como configurar conexão com Meu Pluggy:

1. Criar uma conta em pluggy.ai
2. Fazer login em meu.pluggy.ai e conectar contas bancárias
3. Em dashboard.pluggy.ai > ir em Aplicações > Nova
4. Ir para demo.pluggy.ai

    conectar conta > MeuPluggy (uma instância para cada conta)
    
5. Configurar credenciais no Actual:

    criar uma conta chamada "Pluggy" (pode ser off-budget) e inserir na anotação da conta:

       #clientID: "xxxxx"
       #clientSecret: "xxxxx"
       - informação encontrada em dashboard.pluggy.ai > Aplicações > Credenciais

   inserir o ID nas anotações de cada conta que a ser sincronizada:

       #pluggy "TYPE, itemID, {cardNumber}"
       - TYPE: BANK / CREDIT
       - itemID: encontrado em meu.pluggy.ai > ... > copiar itemID
       - {cardNumber}: 4 dígitos finais do CC (apenas se TYPE = CREDIT)

# Instalação

Criar e configurar arquivo config.ini (ver config-example.ini)
