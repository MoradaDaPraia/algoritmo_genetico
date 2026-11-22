from collections.abc import Callable
from random import Random
from time import perf_counter

Cromossomo = list[int]
Populacao = list[Cromossomo]


# indice de cada classe na matriz de classes
TANQUE = 0
ASSASSINO = 1
MAGO = 2
ATIRADOR = 3
SUPORTE = 4
DRUIDA = 5

# indices de cada atributo.
ATQ = 0
DEF = 1
MAG = 2
AGI = 3
CURA = 4

NOMES_ATRIBUTOS = ("ATQ", "DEF", "MAG", "AGI", "CURA")
NOMES_CLASSES = ("Tanque", "Assassino", "Mago", "Atirador", "Suporte", "Druida")

# guarda os multiplicadores para cada atributo de cada classe
MULTIPLICADORES_POR_CLASSE: tuple[tuple[float, ...], ...] = (
    (0.7, 2.0, 0.2, 0.5, 0.3),  # tanque
    (1.5, 0.5, 0.2, 2.0, 0.1),  # assassino
    (0.2, 0.6, 2.0, 0.7, 0.4),  # mago
    (2.0, 0.7, 0.4, 1.2, 0.2),  # atirador
    (0.4, 0.9, 0.8, 0.6, 2.0),  # suporte
    (0.7, 0.8, 1.2, 0.9, 1.4),  # druida
)

# indices de cada item.
ESPADA_DO_ALVORECER = 0
MANTO_DA_MURALHA = 1
ORBE_DO_VAZIO = 2
ARCO_DAS_TRES_LUAS = 3
GRIMORIO_DE_CINZAS = 4
BOTAS_DO_VENTO = 5
AMULETO_VITAL = 6
MACHADO_RACHAFIRMAMENTO = 7
BROCHE_ECLIPSE = 8
LUPA_ARCANA = 9
ESCUDO_DE_VIME = 10
LIRA_DA_AURORA = 11
ADAGA_SUSSURRO = 12
ANEL_DAS_MARE = 13
CAPA_DO_EXILIO = 14
RAIZ_DE_FERRO = 15
CETRO_DO_CERVO = 16
MANTO_DAS_ESTACOES = 17

NOMES_ITENS = (
    "Espada do Alvorecer",
    "Manto da Muralha",
    "Orbe do Vazio",
    "Arco das Três Luas",
    "Grimório de Cinzas",
    "Botas do Vento",
    "Amuleto Vital",
    "Machado Rachafirmamento",
    "Broche Eclipse",
    "Lupa Arcana",
    "Escudo de Vime",
    "Lira da Aurora",
    "Adaga Sussurro",
    "Anel das Marés",
    "Capa do Exílio",
    "Raiz de Ferro",
    "Cetro do Cervo",
    "Manto das Estações",
)

# atributos que cada item da (itens podem penalizar atributos, estao como negativos)
ATRIBUTOS_ITENS: tuple[tuple[float, ...], ...] = (
    (38, 4, 0, 8, 0),  # espada do Alvorecer
    (0, 42, 0, -4, 6),  # manto da muralha
    (-5, 0, 39, 4, 8),  # orbe do vazio
    (32, 0, 0, 19, 0),  # arco das tres luas
    (0, -3, 43, 0, 9),  # grimório de cinzas
    (8, 0, 0, 30, -2),  # botas do vento
    (0, 15, 12, 0, 24),  # amuleto vital
    (46, 17, -8, -5, 0),  # machado rachafirmamento
    (12, 12, 12, 12, 12),  # broche eclipse
    (0, 5, 34, 13, 4),  # lupa arcana
    (-4, 36, 0, 8, 5),  # escudo de vime
    (4, 8, 14, 10, 27),  # lira da aurora
    (29, -6, 0, 23, 0),  # adaga sussurro
    (9, 11, 10, 8, 13),  # anel das mares
    (6, 18, 16, 7, 19),  # capa do exilio
    (12, 22, 8, -2, 14),  # raiz de ferro
    (4, 6, 24, 8, 20),  # cetro do cervo
    (8, 12, 13, 11, 15),  # manto das estações
)

QUANTIDADE_IENS = len(ATRIBUTOS_ITENS)
QUANTIDADE_CLASSES = len(MULTIPLICADORES_POR_CLASSE)
ITENS_POR_PERSONAGEM = 3
TAMANHO_CROMOSSOMO = QUANTIDADE_CLASSES * ITENS_POR_PERSONAGEM
LIMITE_ESTAGNACAO = 50
PROPORCAO_MENOR_ATRIBUTO = 0.15
TAXA_PENALIDADE_BALANCEAMENTO = 0.02
PROPORCAO_MENOR_ATRIBUTO_HARD = 0.01
PENALIDADE_HARD_CONSTRAINT = 1_000_000.0


class AlgoritmoGenetico:
    def __init__(
        self,
        random: Random | None = None,
        tamanho_populacao: int = 200,
        taxa_elitismo: float = 0.05,
        taxa_cruzamento: float = 0.80,
        taxa_mutacao: float = 0.05,
    ) -> None:
        # inicializa valores
        self._random = random or Random()
        self._tamanho_populacao = tamanho_populacao
        self._taxa_elitismo = taxa_elitismo
        self._taxa_cruzamento = taxa_cruzamento
        self._taxa_mutacao = taxa_mutacao
        self._populacao = self.inicializar_populacao()
        self.ordenar_populacao()

    def inicializar_populacao(self) -> Populacao:
        # inicializa a populacao com itens aleatorios para cada classe
        return [
            self._random.sample(range(QUANTIDADE_IENS), QUANTIDADE_IENS)
            for _ in range(self._tamanho_populacao)
        ]

    def avaliar_cromossomo(self, cromossomo: Cromossomo) -> float:
        # avalia um cromossomo somando as avaliacoes de cada classe
        return sum(
            self.avaliar_classe(cromossomo, indice_classe)
            for indice_classe in range(QUANTIDADE_CLASSES)
        )

    def calcular_atributos(
        self, cromossomo: Cromossomo, indice_classe: int
    ) -> dict[str, float]:
        # calcula os atributos da classe com base nos itens e multiplicadores
        multiplicadores = MULTIPLICADORES_POR_CLASSE[indice_classe]
        indice_inicial = indice_classe * ITENS_POR_PERSONAGEM
        indices_itens_personagem = cromossomo[
            indice_inicial : indice_inicial + ITENS_POR_PERSONAGEM
        ]

        # retorna um dicionario com o nome do atributo e seu valor
        return {
            NOMES_ATRIBUTOS[indice_atributo]: sum(
                ATRIBUTOS_ITENS[indice_item][indice_atributo]
                * multiplicadores[indice_atributo]
                for indice_item in indices_itens_personagem
            )
            for indice_atributo in range(len(NOMES_ATRIBUTOS))
        }

    def avaliar_classe(self, cromossomo: Cromossomo, indice_classe: int) -> float:
        # primeiro, soma todos os atributos e subtrai pela penalizacao do desbalanceamento
        avaliacao = sum(
            self.calcular_atributos(cromossomo, indice_classe).values()
        ) - self.penalizar_balanceamento(cromossomo, indice_classe)

        # ve se tem alguma violacao hard e aplica penalizacao
        violacao = self.calcular_violacao_hard(cromossomo, indice_classe)
        if violacao > 0:
            # esse calculo sempre vai puxar o avaliação para o extremo do negativo
            # serve para dizer que não aceitamos essa solucao como valida
            avaliacao -= PENALIDADE_HARD_CONSTRAINT * (1 + violacao)

        return avaliacao

    def calcular_violacao_hard(
        self, cromossomo: Cromossomo, indice_classe: int
    ) -> float:
        # obtem o maior e o menor atributo
        valores_atributos_personagem = list(
            self.calcular_atributos(cromossomo, indice_classe).values()
        )
        maior_atributo = max(0.0, max(valores_atributos_personagem))
        menor_atributo = min(valores_atributos_personagem)

        # verifica se o menor atributo está dentro da janela requerida
        minimo_requerido = PROPORCAO_MENOR_ATRIBUTO_HARD * maior_atributo
        diferenca = max(0.0, minimo_requerido - menor_atributo)

        # retorna a escala da violacao proporcional ao maior atributo
        return diferenca / max(maior_atributo, 1.0)

    def penalizar_balanceamento(
        self, cromossomo: Cromossomo, class_index: int
    ) -> float:
        # obtem maior e menor atributo
        valores_atributos_personagem = list(
            self.calcular_atributos(cromossomo, class_index).values()
        )
        maior_atributo = max(0.0, max(valores_atributos_personagem))
        menor_atributo = min(valores_atributos_personagem)

        # verifica se esta dentro da janela de penalizacao
        diferenca = max(0.0, PROPORCAO_MENOR_ATRIBUTO * maior_atributo - menor_atributo)

        # retorna a penalizacao proporcional ao quadrado da diferenca
        return TAXA_PENALIDADE_BALANCEAMENTO * diferenca**2

    def ordenar_populacao(self) -> None:
        # ordena a populacao pelos de maior avaliacao primeiro
        self._populacao.sort(key=self.avaliar_cromossomo, reverse=True)

    def selecionar_elite(self) -> Populacao:
        # calcula a quantidade de individuos pela taxa e recorta os melhores
        quantidade = round(self._tamanho_populacao * self._taxa_elitismo)
        return [cromossomo.copy() for cromossomo in self._populacao[:quantidade]]

    def calcular_pesos(self) -> list[float]:
        # calcula as avaliacoes
        avaliacoes = [
            self.avaliar_cromossomo(cromossomo) for cromossomo in self._populacao
        ]

        # guarda os indices dos validos e invalidos
        validade_cromossomos = [avaliacao >= 0 for avaliacao in avaliacoes]
        indices_validos = [
            indice for indice, valido in enumerate(validade_cromossomos) if valido
        ]
        indices_invalidos = [
            indice for indice, valido in enumerate(validade_cromossomos) if not valido
        ]
        # inicializa a lista de pesos
        pesos = [0.0] * len(self._populacao)

        if not indices_validos:
            # se nao tiver nenhuma valida, favorece as melhores dentre as invalidas
            menor_avaliacao = min(avaliacoes)
            pesos = [avaliacao - menor_avaliacao for avaliacao in avaliacoes]
        else:
            # preenche os pesos para os indices validos
            for indice in indices_validos:
                pesos[indice] = avaliacoes[indice]

            # o maior peso invalido tera metade da pontuacao do menor valido
            menor_peso_valido = min(pesos[indice] for indice in indices_validos)
            limite_peso_invalido = menor_peso_valido * 0.5

            # so calcula se tiver algum indice invalido
            if indices_invalidos:
                # calcula o intervalo entre a maior e a menor avaliacao
                menor_avaliacao_invalida = min(
                    avaliacoes[indice] for indice in indices_invalidos
                )
                maior_avaliacao_invalida = max(
                    avaliacoes[indice] for indice in indices_invalidos
                )
                intervalo = maior_avaliacao_invalida - menor_avaliacao_invalida

                for indice in indices_invalidos:
                    # se o intervalo for zero é porque todos os invalidos sao iguais, aplica 0.5 direto
                    if intervalo == 0:
                        proporcao = 0.5
                    else:
                        # pega a diferenca entre o menor e o atual
                        diferenca = avaliacoes[indice] - menor_avaliacao_invalida
                        # divide pelo intervalo entre o menor e o maior
                        proporcao = diferenca / intervalo

                    # aplica o limite de 0.5 na proporcao calculada
                    pesos[indice] = limite_peso_invalido * proporcao

        # normaliza os pesos para que a soma de todos fique 1
        total = sum(pesos)
        return [peso / total for peso in pesos]

    def sortear_parente(self, pesos: list[float]) -> Cromossomo:
        # numero aleatorio entre 0 e 1
        chance = self._random.random()
        acumulador = 0.0

        # seleciona um qualquer ate escolher de verdade
        escolhido = self._populacao[-1]

        # acumula ate passar da chance aleatoria
        for cromossomo, peso in zip(self._populacao, pesos):
            acumulador += peso
            if chance <= acumulador:
                escolhido = cromossomo
                break

        return escolhido

    def selecionar_parentes(self) -> Populacao:
        pesos = self.calcular_pesos()
        # seleciona candidatos para cruzamento pelo metodo da roleta
        return [self.sortear_parente(pesos) for _ in range(self._tamanho_populacao)]

    def cruzar_par(
        self, primeiro_parente: Cromossomo, segundo_parente: Cromossomo
    ) -> tuple[Cromossomo, Cromossomo]:
        # se a chance aleatoria der menor que a taxa de cruzamento, nao cruza
        if self._random.random() >= self._taxa_cruzamento:
            return primeiro_parente.copy(), segundo_parente.copy()

        # pega o inicio e o fim da janela
        inicio, fim = sorted(self._random.sample(range(TAMANHO_CROMOSSOMO), 2))
        # +1 porque o slice de python tem fim exclusivo
        fim += 1

        def gerar_filho(
            parente_segmento: Cromossomo, parente_ordem: Cromossomo
        ) -> Cromossomo:
            # crie a lista do cromossomo novo
            filho: Cromossomo = [-1] * TAMANHO_CROMOSSOMO
            # copia diretamente o segmento do parente
            filho[inicio:fim] = parente_segmento[inicio:fim]

            # guarda os genes ja usados
            usado = set(filho[inicio:fim])
            # itera o outro parente do fim ao inicio pegando todos os genes nao usados
            sobra = [
                gene
                for gene in parente_ordem[fim:] + parente_ordem[:fim]
                if gene not in usado
            ]

            # obtem as posicoes que ainda faltam preencher
            posicoes = list(range(fim, TAMANHO_CROMOSSOMO)) + list(range(0, inicio))

            # coloca as sobras do outro parente nas posicoes que faltam preencher
            for posicao, gene in zip(posicoes, sobra):
                filho[posicao] = gene

            return filho

        # retorna os dois filhos
        return (
            gerar_filho(primeiro_parente, segundo_parente),
            gerar_filho(segundo_parente, primeiro_parente),
        )

    def cruzar_parentes(self, parentes: Populacao, quantidade_filhos: int) -> Populacao:
        # cria uma nova lista que sera a proxima populacao
        filhos: Populacao = []

        # ate atingir a quantidade de filhos
        while len(filhos) < quantidade_filhos:
            # pega aleatoriamente dois parentes
            primeiro_parente = self._random.choice(parentes)
            segundo_parente = self._random.choice(parentes)

            # adiciona os filhos na nova populacao
            primeiro_filho, segundo_filho = self.cruzar_par(
                primeiro_parente, segundo_parente
            )
            filhos.extend((primeiro_filho, segundo_filho))

        # arranca um filho fora caso a quantidade seja impar
        return filhos[:quantidade_filhos]

    def mutar_filhos(self, filhos: Populacao) -> None:
        # itera todos os cromossomos
        for cromossomo in filhos:
            # sorteia um numero de 0-1, vai mutar se for menor que a taxa
            if self._random.random() < self._taxa_mutacao:
                # troca dois genes de lugar no cromossomo
                primeiro, segundo = self._random.sample(range(TAMANHO_CROMOSSOMO), 2)
                cromossomo[primeiro], cromossomo[segundo] = (
                    cromossomo[segundo],
                    cromossomo[primeiro],
                )

    def iterar(self) -> None:
        # itera uma geracao, ciclo do ag
        elite = self.selecionar_elite()
        parentes = self.selecionar_parentes()
        filhos = self.cruzar_parentes(parentes, self._tamanho_populacao - len(elite))
        self.mutar_filhos(filhos)
        self._populacao = filhos + elite
        self.ordenar_populacao()

    def obter_cromossomo(self, local: float = 0.0) -> tuple[Cromossomo, float]:
        # retorna uma copia do cromossomo na posicao relativa 0=melhor, 1=pior
        posicao = round((len(self._populacao) - 1) * local)
        cromossomo = self._populacao[posicao]
        return cromossomo.copy(), self.avaliar_cromossomo(cromossomo)

    def obter_itens(self, cromossomo: Cromossomo) -> dict[str, list[str]]:
        # retorna um dicionario com o nome de cada classe e os nomes dos itens
        return {
            NOMES_CLASSES[indice_classe]: [
                NOMES_ITENS[cromossomo[indice_classe * ITENS_POR_PERSONAGEM + posicao]]
                for posicao in range(ITENS_POR_PERSONAGEM)
            ]
            for indice_classe in range(QUANTIDADE_CLASSES)
        }

    def rodar(
        self,
        limite_estagnacao: int = LIMITE_ESTAGNACAO,
        callback: Callable[[int, 'AlgoritmoGenetico'], None] | None = None,
    ) -> None:
        geracao = 0
        geracoes_estagnadas = 0
        melhor_avaliacao = self.avaliar_cromossomo(self._populacao[0])

        # roda ate estagnar sem melhorar por x rodadas
        while geracoes_estagnadas < limite_estagnacao:
            self.iterar()
            geracao += 1

            melhor_atual = self.avaliar_cromossomo(self._populacao[0])
            if melhor_atual > melhor_avaliacao:
                melhor_avaliacao = melhor_atual
                geracoes_estagnadas = 0
            else:
                geracoes_estagnadas += 1

            if callback is not None:
                callback(geracao, self)


def main() -> None:
    algoritmo_genetico = AlgoritmoGenetico(random=Random(67))

    # printar as avaliacoes gerais da populacao atual
    def printar_geracao(generation: int, ag: AlgoritmoGenetico) -> None:
        _, pior_avaliacao = ag.obter_cromossomo(1.0)
        _, mediana_avaliacao = ag.obter_cromossomo(0.5)
        _, melhor_avaliacao = ag.obter_cromossomo(0.0)
        print(
            f"Geração {generation}: pior = {pior_avaliacao:.2f} | "
            f"mediano = {mediana_avaliacao:.2f} | melhor = {melhor_avaliacao:.2f}"
        )

    # printar performance do algoritmo
    inicio_ag = perf_counter()
    algoritmo_genetico.rodar(
        limite_estagnacao=LIMITE_ESTAGNACAO, callback=printar_geracao
    )
    tempo_ag = perf_counter() - inicio_ag
    print(f"Tempo do algoritmo genético: {tempo_ag:.4f} segundos")

    # printar avaliacao do melhor cromossomo
    melhor, avaliacao = algoritmo_genetico.obter_cromossomo()
    print(f"\nMelhor avaliação: {avaliacao:.2f}")
    for indice_classe, (nome_classe, itens) in enumerate(
        algoritmo_genetico.obter_itens(melhor).items()
    ):
        atributos = algoritmo_genetico.calcular_atributos(melhor, indice_classe)
        penalidade_balanceamento = algoritmo_genetico.penalizar_balanceamento(
            melhor, indice_classe
        )
        avaliacao_classe = algoritmo_genetico.avaliar_classe(melhor, indice_classe)

        print(f"\n{nome_classe} (avaliação {avaliacao_classe:.2f})")
        print(f"  Itens: {', '.join(itens)}")
        print(
            "  Atributos: "
            + " | ".join(f"{nome}={valor:.2f}" for nome, valor in atributos.items())
        )
        print(f"  Penalidade por desbalanceamento: {penalidade_balanceamento:.2f}")

    print(f"\nAvaliação total da equipe: {avaliacao:.2f}")


if __name__ == "__main__":
    main()
