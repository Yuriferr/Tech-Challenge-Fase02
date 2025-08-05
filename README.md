# Tech Challenge - Fase 2: Otimizador de Times com Algoritmos Genéticos

Este projeto foi desenvolvido como parte do Tech Challenge da Pós-Graduação em "IA para Devs". O objetivo é utilizar Algoritmos Genéticos (AG) para resolver um problema complexo de otimização: a escalação ideal de um time de futebol.

## 1. O Problema: Definição e Objetivos

O desafio consiste em, a partir de um elenco completo de um time, determinar a melhor combinação possível entre:
1.  A **formação tática** a ser utilizada (ex: 4-4-2, 4-3-3, etc.).
2.  A **escalação de 11 jogadores** com a habilidade mais adequada para preencher as posições dessa formação.

O objetivo principal é **maximizar a "Pontuação de Fitness"** da equipe, uma métrica que representa a força e a coerência tática do time. Um critério de sucesso é gerar escalações que sejam não apenas fortes individualmente, mas que também respeitem a especialidade de cada jogador, evitando improvisações que prejudiquem o desempenho coletivo.

Foi utilizado no projeto a base do FIFA22 baixada do Kaggle. Link de referência da base: [FIFA 22 complete player dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset).

## 2. Abordagem e Implementação do Algoritmo

A solução foi implementada em Python, utilizando a biblioteca `Tkinter` para a interface gráfica e `pandas` para a manipulação de dados. A estrutura do AG foi organizada da seguinte forma:

* **Representação da Solução (Genoma):** Cada solução candidata (um "indivíduo") é representada por um dicionário Python contendo a formação tática e uma lista com os 11 jogadores escalados.

* **Função de Fitness:** Ela avalia a qualidade de cada time calculando a soma das pontuações efetivas dos jogadores. A pontuação efetiva é o `overall` do jogador multiplicado por um fator de aptidão posicional, que penaliza fortemente jogadores fora de posição.
O `overall` no FIFA refere-se à classificação geral de um jogador, um número que indica a habilidade e o desempenho do jogador no jogo. Essa pontuação é calculada com base em várias estatísticas e atributos, como velocidade, chute, passe, drible, defesa e físico. Quanto maior o overall, mais forte e eficiente o jogador será no jogo.

* **Método de Inicialização:** A população inicial é gerada de forma totalmente aleatória, criando diversas combinações de táticas e jogadores para garantir uma ampla exploração do espaço de busca.

* **Método de Seleção:** Foi utilizado o **Elitismo**. Os 20% melhores indivíduos de cada geração são preservados e passam a ser os pais da geração seguinte, garantindo que as melhores soluções encontradas não se percam.

* **Método de Crossover:** Um método híbrido que combina a formação de um dos pais com uma escalação gerada pelo cruzamento de ponto único dos jogadores de ambos os pais.

* **Método de Mutação:** Para introduzir diversidade, uma pequena chance (20%) de mutação permite a troca de um jogador da escalação por outro do banco, explorando novas possibilidades.

* **Critério de Parada:** O algoritmo é projetado para rodar continuamente, permitindo que o usuário observe a evolução e decida o momento ideal de parar a otimização através de um botão na interface.

## 3. Como Executar o Projeto

Para rodar a aplicação, siga os passos abaixo:

**Pré-requisitos:**
* Python 3.x instalado.
* O arquivo de dados `players_22.csv`, que pode ser baixado do Kaggle: [FIFA 22 complete player dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset).
* Uma imagem de campo de futebol salva como `soccer_field.png` na mesma pasta do projeto.

**Passos:**
1.  Clone este repositório para a sua máquina local.
2.  Abra um terminal na pasta do projeto e instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  Execute o arquivo principal da aplicação:
    ```bash
    python app.py
    ```

## 4. Testes e Resultados

A eficácia do algoritmo é demonstrada diretamente na interface da aplicação:

* **Gráfico em Tempo Real:** O gráfico exibe a pontuação de fitness do melhor indivíduo (linha azul escura) e a média da população (linha azul clara) a cada geração. É possível observar uma rápida convergência para soluções de alta qualidade.
* **Resultados Coerentes:** As escalações finais geradas são taticamente lógicas e fortes, alocando jogadores renomados em suas posições de ofício e escolhendo formações que se adequam ao elenco disponível.
* **Comparativo com Métodos Convencionais:** Enquanto um técnico se baseia na intuição, o AG realiza um teste massivo de milhares de combinações em segundos, encontrando uma solução matematicamente otimizada com base nos critérios definidos, o que representa uma abordagem mais robusta e baseada em dados.

## 5. Conclusão

O projeto demonstrou com sucesso a aplicação de Algoritmos Genéticos para resolver um problema de otimização do mundo real. O sistema é capaz de processar um grande volume de dados e encontrar soluções de alta qualidade de forma eficiente, entregando uma ferramenta prática e funcional para análise tática de equipes de futebol.
