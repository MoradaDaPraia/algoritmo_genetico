# Algoritmo genético para montar uma equipe de RPG

## Problema

O objetivo é distribuir 18 itens únicos entre seis personagens: Tanque,
Assassino, Mago, Atirador, Suporte e Druida. Cada personagem recebe exatamente
três itens, e todos os itens precisam ser usados.

Os itens aumentam ou reduzem cinco atributos: ATQ, DEF, MAG, AGI e CURA. Cada
classe tem multiplicadores próprios para esses atributos. A avaliação da equipe
considera os atributos dos itens depois da aplicação desses multiplicadores e
penaliza personagens muito desbalanceados. Há também um limite mínimo de 1% do
maior atributo para o menor atributo efetivo de cada personagem.

## Representação da solução

Um cromossomo é uma sequência de 18 índices, cada um representando um item. As
posições são agrupadas em blocos de três por personagem. Assim, os três
primeiros itens pertencem ao Tanque, os três seguintes ao Assassino e assim por
diante. Cada índice de item aparece uma única vez no cromossomo.

## Algoritmo genético

A seleção de pais usa roleta, dando mais chance a cromossomos com melhor
avaliação. O cruzamento usa OX (Order Crossover): copia um trecho de um dos pais
e completa o filho com os itens do outro pai na ordem em que aparecem,
ignorando os itens que já foram copiados. Isso mantém cada item exatamente uma
vez no cromossomo.

A mutação troca as posições de dois itens, preservando a regra de usar todos os
itens. A busca termina após 20 gerações consecutivas sem melhora.

## Requesitos

Python 3.12.4+

## Como rodar

O código não usa nenhuma biblioteca além das padrão do python. Funciona apenas
rodando:

```sh
python main.py
```