# Trabalho de Tópicos Avancados 2

> Usar pelo menos 5 IAs diferentes (entre pagas e gratuitas) para fazer uma análise dos processos catalogados. As equipes devem definir prompt e ir ajustando, de forma interativa, até achar resultados satisfatórios. É importante usar as técnicas de prompt engineering, considerar valores de temperatura, top-p e top-k, etc.
> A equipe deve apresentar um relatório textual desse estudo, descrevendo todo o método utilizado e os resultados alcançados. Olhar o TCC do aurora para se basear.
> A equipe deve fazer uma apresentação sobre o trabalho. Duração de até 10 minutos.
> Todos os alunos devem apresentar.

## Como Funciona?

OBJETIVO: descobrir qual melhor prompt e ia na leitura dos pdf de forma sistemática.

Com a base de dados de 50 pdfs, usando um prompt para ia(s) para descrever como uma ia deveria buscar pelos pontos destacados nas resolucoes da lista

utilizar esse pompt modificado de multiplas maneiras para extracao de dados de todos os 50 pdfs

prompt para ia comparar a semelhanca das duas saídas

Gemini + Groq Cloud + Mistral AI

### Método de Avaliação dos Dados

> [TODO]

## Todo

- termino do planejamento concreto do prompt 1 + 2
- criação do codigo no script em ./scr/main.py ou outros para acesso da(s) api(s) necessárias para o processamento dos dados
- encontrar uma estratégia pra calcular a acurácia (percentual) de cada prompt e IA, e depois a média do total. pode ser várias de uma mesma IA, mas modelo diferente (Ex: Spring Ai -> Python + PydanticAI)
- criar o prompt pra as regras igual foi no trabalho anterior
