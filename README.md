# Actual-Pluggy-py

Brazilian Bank Sync for Actual with Pluggy using Python

# Como configurar conexão com Meu Pluggy:

1. criar uma conta em pluggy.ai
    ir em Aplicações > Nova

2. fazer login em meu.pluggy.ai e conectar contas bancárias

3. ir para demo.pluggy.ai
    conectar conta > MeuPluggy 
    repetir para quantas contas existir
    
4. configurar credenciais no Actual:
    criar uma conta chamada "Pluggy" (pode ser off-budget)
    inserir na anotação da conta:
        #clientID: "xxxxx"
        #clientSecret: "xxxxx"
        disponível em dashboard.pluggy.ai > Aplicações > Credenciais
    inserir ID em casa conta que deseja sincronizar:
        #pluggy "TYPE, itemID"
            TYPE = BANK / CREDIT
            itemID -> disponível em meu.pluggy.ai > ... > copiar itemID
