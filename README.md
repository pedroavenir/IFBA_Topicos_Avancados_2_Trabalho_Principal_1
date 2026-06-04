# Trabalho de Tópicos Avancados 2

> Usar pelo menos 5 IAs diferentes (entre pagas e gratuitas) para fazer uma análise dos processos catalogados. As equipes devem definir prompt e ir ajustando, de forma interativa, até achar resultados satisfatórios. É importante usar as técnicas de prompt engineering, considerar valores de temperatura, top-p e top-k, etc.
> A equipe deve apresentar um relatório textual desse estudo, descrevendo todo o método utilizado e os resultados alcançados. Olhar o TCC do aurora para se basear.
> A equipe deve fazer uma apresentação sobre o trabalho. Duração de até 10 minutos.
> Todos os alunos devem apresentar.

## Como Funciona?

OBJETIVO: descobrir qual melhor prompt e ia na leitura dos pdf de forma sistemática.

+- 50 pdf com as saídas esperadas -> IA + PROMPT  -> saída p/ cada pdf -> comparar com o resultado esperado (IA + PROMPT2)
(SAÍDA DE FORMA PADRONIZADA JSON)

Gemini + outras IAs caso possivel

### Método de Avaliação dos Dados

> [TODO]

## Todo

- Formatar a planilha em json para acessar mais facilmente os dados no codigo principal, colocar o script ou arquivos neecssario para isso no ./src/preprocessing
- termino do planejamento concreto do prompt 1 + 2
- procura profunda pelos modelos de IA que usaremos com API de preco acessivel
- criação do codigo no script em ./scr/main.py ou outros para acesso da(s) api(s) necessárias para o processamento dos dados
- encontrar uma estratégia pra calcular a acurácia (percentual) de cada prompt e IA, e depois a média do total. pode ser várias de uma mesma IA, mas modelo diferente (Ex: Spring Ai -> Python + PydanticAI)
- criar o prompt pra as regras igual foi no trabalho anterior
- renomear os pdfs se necessario para remover as iregularidades ou arquivos cujo nome nao esta na tabela (melhor renomear cada pdf com apenas o seu ID)
