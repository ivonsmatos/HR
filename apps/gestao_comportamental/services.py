"""
SyncRH - Gestão Comportamental - Services
=========================================
Camada de serviços com lógica de negócio para análise DISC
"""

from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
import logging
import math

logger = logging.getLogger(__name__)


class ProfilerService:
    """Serviço para aplicação do profiler DISC"""
    
    @staticmethod
    @transaction.atomic
    def iniciar_aplicacao(colaborador, questionario, contexto=None):
        """Inicia aplicação do questionário profiler"""
        from .models import AplicacaoProfiler
        
        # Verifica se há aplicação pendente
        pendente = AplicacaoProfiler.objects.filter(
            colaborador=colaborador,
            questionario=questionario,
            status='em_andamento'
        ).first()
        
        if pendente:
            return pendente
        
        aplicacao = AplicacaoProfiler.objects.create(
            colaborador=colaborador,
            questionario=questionario,
            contexto=contexto or 'avaliacao',
            status='em_andamento',
            data_inicio=timezone.now()
        )
        
        logger.info(f"Aplicação profiler iniciada: {aplicacao.id}")
        return aplicacao
    
    @staticmethod
    def registrar_resposta(aplicacao, questao, opcao_mais, opcao_menos, tempo=None):
        """Registra resposta de uma questão"""
        from .models import RespostaProfiler
        
        resposta, created = RespostaProfiler.objects.update_or_create(
            aplicacao=aplicacao,
            questao=questao,
            defaults={
                'opcao_mais': opcao_mais,
                'opcao_menos': opcao_menos,
                'tempo_resposta': tempo
            }
        )
        
        return resposta
    
    @staticmethod
    @transaction.atomic
    def finalizar_aplicacao(aplicacao):
        """Finaliza aplicação e calcula perfil DISC"""
        from .models import RespostaProfiler
        
        # Verifica se todas as questões obrigatórias foram respondidas
        questoes_obrigatorias = aplicacao.questionario.questoes.filter(
            obrigatoria=True
        ).count()
        
        respostas = RespostaProfiler.objects.filter(
            aplicacao=aplicacao
        ).count()
        
        if respostas < questoes_obrigatorias:
            raise ValueError(
                f"Faltam {questoes_obrigatorias - respostas} questões obrigatórias"
            )
        
        # Calcula tempo total
        aplicacao.tempo_total = (
            timezone.now() - aplicacao.data_inicio
        ).total_seconds() // 60
        
        aplicacao.status = 'concluido'
        aplicacao.data_conclusao = timezone.now()
        aplicacao.save()
        
        # Calcula perfil DISC
        perfil = DISCCalculatorService.calcular_perfil(aplicacao)
        
        return {
            'aplicacao': aplicacao,
            'perfil': perfil
        }


class DISCCalculatorService:
    """Serviço para cálculo do perfil DISC"""
    
    # Pesos das dimensões DISC por tipo de opção
    PESOS_DISC = {
        'D': {'assertivo': 2, 'direto': 2, 'competitivo': 1.5, 'decisivo': 1.5},
        'I': {'entusiasta': 2, 'comunicativo': 2, 'otimista': 1.5, 'sociavel': 1.5},
        'S': {'paciente': 2, 'cooperativo': 2, 'estavel': 1.5, 'leal': 1.5},
        'C': {'analitico': 2, 'preciso': 2, 'sistematico': 1.5, 'cauteloso': 1.5}
    }
    
    # Padrões DISC combinados
    PADROES = {
        'DC': 'Realizador',
        'DI': 'Inspirador',
        'DS': 'Comandante',
        'ID': 'Promotor',
        'IC': 'Conselheiro',
        'IS': 'Relacionador',
        'SC': 'Especialista',
        'SD': 'Agente',
        'SI': 'Apoiador',
        'CD': 'Pensador',
        'CI': 'Avaliador',
        'CS': 'Perfeccionista'
    }
    
    @staticmethod
    @transaction.atomic
    def calcular_perfil(aplicacao):
        """Calcula perfil DISC baseado nas respostas"""
        from .models import PerfilDISC, RespostaProfiler
        
        respostas = RespostaProfiler.objects.filter(aplicacao=aplicacao)
        
        # Contadores para cada dimensão
        scores = {
            'D': {'natural': 0, 'adaptado': 0},
            'I': {'natural': 0, 'adaptado': 0},
            'S': {'natural': 0, 'adaptado': 0},
            'C': {'natural': 0, 'adaptado': 0}
        }
        
        for resposta in respostas:
            # Processa opção "mais" (perfil natural)
            if resposta.opcao_mais:
                dimensao = DISCCalculatorService._identificar_dimensao(
                    resposta.opcao_mais
                )
                if dimensao:
                    scores[dimensao]['natural'] += 1
            
            # Processa opção "menos" (perfil adaptado - inverso)
            if resposta.opcao_menos:
                dimensao = DISCCalculatorService._identificar_dimensao(
                    resposta.opcao_menos
                )
                if dimensao:
                    # Adiciona às outras dimensões
                    for d in ['D', 'I', 'S', 'C']:
                        if d != dimensao:
                            scores[d]['adaptado'] += 0.33
        
        # Normaliza para escala 0-100
        total_questoes = respostas.count() or 1
        
        d_score = round((scores['D']['natural'] / total_questoes) * 100)
        i_score = round((scores['I']['natural'] / total_questoes) * 100)
        s_score = round((scores['S']['natural'] / total_questoes) * 100)
        c_score = round((scores['C']['natural'] / total_questoes) * 100)
        
        # Determina perfil principal
        perfil_principal = max(
            [('D', d_score), ('I', i_score), ('S', s_score), ('C', c_score)],
            key=lambda x: x[1]
        )[0]
        
        # Determina padrão (combinação das duas maiores)
        ordenado = sorted(
            [('D', d_score), ('I', i_score), ('S', s_score), ('C', c_score)],
            key=lambda x: x[1],
            reverse=True
        )
        padrao_key = ordenado[0][0] + ordenado[1][0]
        padrao = DISCCalculatorService.PADROES.get(padrao_key, 'Misto')
        
        # Calcula intensidade
        intensidade = DISCCalculatorService._calcular_intensidade(
            d_score, i_score, s_score, c_score
        )
        
        # Cria perfil
        perfil = PerfilDISC.objects.create(
            aplicacao=aplicacao,
            tipo_perfil='natural',
            dominancia=d_score,
            influencia=i_score,
            estabilidade=s_score,
            conformidade=c_score,
            perfil_principal=perfil_principal,
            padrao=padrao,
            intensidade=intensidade
        )
        
        # Gera descrições
        DISCCalculatorService._gerar_descricoes(perfil)
        
        return perfil
    
    @staticmethod
    def _identificar_dimensao(opcao):
        """Identifica dimensão DISC de uma opção"""
        # Mapeamento simplificado
        mapeamento = {
            'assertivo': 'D', 'direto': 'D', 'competitivo': 'D', 'decisivo': 'D',
            'entusiasta': 'I', 'comunicativo': 'I', 'otimista': 'I', 'sociavel': 'I',
            'paciente': 'S', 'cooperativo': 'S', 'estavel': 'S', 'leal': 'S',
            'analitico': 'C', 'preciso': 'C', 'sistematico': 'C', 'cauteloso': 'C'
        }
        
        if hasattr(opcao, 'texto'):
            texto = opcao.texto.lower()
            for palavra, dimensao in mapeamento.items():
                if palavra in texto:
                    return dimensao
        
        return None
    
    @staticmethod
    def _calcular_intensidade(d, i, s, c):
        """Calcula intensidade do perfil"""
        media = (d + i + s + c) / 4
        variancia = sum((x - media) ** 2 for x in [d, i, s, c]) / 4
        desvio = math.sqrt(variancia)
        
        if desvio > 25:
            return 'muito_alto'
        elif desvio > 15:
            return 'alto'
        elif desvio > 10:
            return 'moderado'
        return 'baixo'
    
    @staticmethod
    def _gerar_descricoes(perfil):
        """Gera descrições do perfil"""
        descricoes = {
            'D': {
                'descricao': 'Perfil orientado a resultados, desafios e tomada de decisão rápida.',
                'pontos_fortes': 'Determinação, iniciativa, foco em resultados, liderança',
                'areas_desenvolvimento': 'Paciência, escuta ativa, trabalho em equipe',
                'estilo_comunicacao': 'Direto, objetivo, focado em resultados',
                'ambiente_ideal': 'Desafiador, com autonomia e oportunidades de liderança',
                'fatores_motivacao': 'Desafios, autoridade, resultados tangíveis',
                'fatores_estresse': 'Rotina, falta de controle, detalhes excessivos'
            },
            'I': {
                'descricao': 'Perfil orientado a pessoas, relacionamentos e comunicação.',
                'pontos_fortes': 'Comunicação, entusiasmo, networking, persuasão',
                'areas_desenvolvimento': 'Organização, foco, follow-up',
                'estilo_comunicacao': 'Expressivo, entusiasta, inspirador',
                'ambiente_ideal': 'Colaborativo, dinâmico, com reconhecimento',
                'fatores_motivacao': 'Reconhecimento social, novidades, interação',
                'fatores_estresse': 'Isolamento, rotina, rejeição'
            },
            'S': {
                'descricao': 'Perfil orientado a estabilidade, cooperação e suporte.',
                'pontos_fortes': 'Paciência, lealdade, trabalho em equipe, consistência',
                'areas_desenvolvimento': 'Adaptação a mudanças, assertividade',
                'estilo_comunicacao': 'Calmo, paciente, bom ouvinte',
                'ambiente_ideal': 'Estável, cooperativo, com relacionamentos duradouros',
                'fatores_motivacao': 'Segurança, harmonia, reconhecimento sincero',
                'fatores_estresse': 'Mudanças bruscas, conflitos, pressão'
            },
            'C': {
                'descricao': 'Perfil orientado a qualidade, precisão e análise.',
                'pontos_fortes': 'Análise, precisão, organização, qualidade',
                'areas_desenvolvimento': 'Flexibilidade, velocidade de decisão',
                'estilo_comunicacao': 'Detalhado, preciso, baseado em dados',
                'ambiente_ideal': 'Estruturado, com padrões claros e tempo para análise',
                'fatores_motivacao': 'Qualidade, conhecimento, processos definidos',
                'fatores_estresse': 'Ambiguidade, erros, pressão por decisões rápidas'
            }
        }
        
        desc = descricoes.get(perfil.perfil_principal, descricoes['S'])
        
        perfil.descricao_perfil = desc['descricao']
        perfil.pontos_fortes = desc['pontos_fortes']
        perfil.areas_desenvolvimento = desc['areas_desenvolvimento']
        perfil.estilo_comunicacao = desc['estilo_comunicacao']
        perfil.ambiente_ideal = desc['ambiente_ideal']
        perfil.fatores_motivacao = desc['fatores_motivacao']
        perfil.fatores_estresse = desc['fatores_estresse']
        perfil.save()


class MatchService:
    """Serviço para cálculo de match comportamental"""
    
    @staticmethod
    def calcular_match(perfil_disc, perfil_ideal):
        """Calcula match entre perfil DISC e perfil ideal do cargo"""
        from .models import MatchComportamental
        
        # Calcula match por dimensão
        match_d = MatchService._calcular_match_dimensao(
            perfil_disc.dominancia,
            perfil_ideal.dominancia_min,
            perfil_ideal.dominancia_max
        )
        
        match_i = MatchService._calcular_match_dimensao(
            perfil_disc.influencia,
            perfil_ideal.influencia_min,
            perfil_ideal.influencia_max
        )
        
        match_s = MatchService._calcular_match_dimensao(
            perfil_disc.estabilidade,
            perfil_ideal.estabilidade_min,
            perfil_ideal.estabilidade_max
        )
        
        match_c = MatchService._calcular_match_dimensao(
            perfil_disc.conformidade,
            perfil_ideal.conformidade_min,
            perfil_ideal.conformidade_max
        )
        
        # Calcula match geral (média ponderada)
        match_geral = (match_d + match_i + match_s + match_c) / 4
        
        # Determina classificação
        classificacao = MatchService._classificar_match(match_geral)
        
        # Identifica gaps
        gaps = MatchService._identificar_gaps(
            perfil_disc, perfil_ideal,
            match_d, match_i, match_s, match_c
        )
        
        # Cria ou atualiza match
        match, created = MatchComportamental.objects.update_or_create(
            perfil_disc=perfil_disc,
            perfil_ideal=perfil_ideal,
            defaults={
                'match_dominancia': match_d,
                'match_influencia': match_i,
                'match_estabilidade': match_s,
                'match_conformidade': match_c,
                'match_geral': match_geral,
                'classificacao': classificacao,
                'gaps_identificados': gaps
            }
        )
        
        # Gera recomendações
        MatchService._gerar_recomendacoes(match)
        
        return match
    
    @staticmethod
    def _calcular_match_dimensao(valor, minimo, maximo):
        """Calcula match de uma dimensão"""
        valor = float(valor)
        minimo = float(minimo)
        maximo = float(maximo)
        
        if minimo <= valor <= maximo:
            return 100.0
        
        if valor < minimo:
            diferenca = minimo - valor
        else:
            diferenca = valor - maximo
        
        # Penaliza proporcionalmente à distância
        match = max(0, 100 - (diferenca * 2))
        
        return round(match, 1)
    
    @staticmethod
    def _classificar_match(match_geral):
        """Classifica nível de match"""
        if match_geral >= 85:
            return 'excelente'
        elif match_geral >= 70:
            return 'bom'
        elif match_geral >= 50:
            return 'moderado'
        return 'baixo'
    
    @staticmethod
    def _identificar_gaps(perfil, ideal, md, mi, ms, mc):
        """Identifica gaps entre perfil e ideal"""
        gaps = []
        
        if md < 70:
            gaps.append({
                'dimensao': 'Dominância',
                'match': md,
                'atual': float(perfil.dominancia),
                'ideal_min': float(ideal.dominancia_min),
                'ideal_max': float(ideal.dominancia_max)
            })
        
        if mi < 70:
            gaps.append({
                'dimensao': 'Influência',
                'match': mi,
                'atual': float(perfil.influencia),
                'ideal_min': float(ideal.influencia_min),
                'ideal_max': float(ideal.influencia_max)
            })
        
        if ms < 70:
            gaps.append({
                'dimensao': 'Estabilidade',
                'match': ms,
                'atual': float(perfil.estabilidade),
                'ideal_min': float(ideal.estabilidade_min),
                'ideal_max': float(ideal.estabilidade_max)
            })
        
        if mc < 70:
            gaps.append({
                'dimensao': 'Conformidade',
                'match': mc,
                'atual': float(perfil.conformidade),
                'ideal_min': float(ideal.conformidade_min),
                'ideal_max': float(ideal.conformidade_max)
            })
        
        return gaps
    
    @staticmethod
    def _gerar_recomendacoes(match):
        """Gera recomendações baseadas no match"""
        recomendacoes = []
        
        if match.classificacao == 'excelente':
            recomendacoes.append('Excelente adequação ao perfil do cargo')
            recomendacoes.append('Candidato prioritário para a posição')
        elif match.classificacao == 'bom':
            recomendacoes.append('Boa adequação ao perfil do cargo')
            if match.gaps_identificados:
                recomendacoes.append('Considerar desenvolvimento nas áreas de gap')
        elif match.classificacao == 'moderado':
            recomendacoes.append('Adequação moderada - avaliar outros fatores')
            recomendacoes.append('Desenvolvimento necessário em algumas áreas')
        else:
            recomendacoes.append('Baixa adequação ao perfil do cargo')
            recomendacoes.append('Considerar outras posições mais adequadas')
        
        match.recomendacoes = recomendacoes
        match.save()


class TimeAnalysisService:
    """Serviço para análise comportamental de times"""
    
    @staticmethod
    def analisar_time(departamento):
        """Analisa composição comportamental do time"""
        from .models import ComparacaoTime, PerfilDISC
        from apps.departamento_pessoal.models import Colaborador
        
        colaboradores = Colaborador.objects.filter(
            departamento=departamento,
            status='ativo'
        )
        
        perfis = []
        for colaborador in colaboradores:
            # Busca último perfil DISC
            perfil = PerfilDISC.objects.filter(
                aplicacao__colaborador=colaborador,
                aplicacao__status='concluido'
            ).order_by('-created_at').first()
            
            if perfil:
                perfis.append(perfil)
        
        if not perfis:
            return None
        
        # Calcula distribuição
        distribuicao = TimeAnalysisService._calcular_distribuicao(perfis)
        
        # Identifica gaps e pontos fortes
        analise = TimeAnalysisService._analisar_composicao(distribuicao)
        
        # Cria comparação
        comparacao = ComparacaoTime.objects.create(
            nome=f'Análise {departamento.nome} - {timezone.now().date()}',
            departamento=departamento,
            mapa_time={
                'perfis': [p.id for p in perfis],
                'distribuicao': distribuicao
            },
            distribuicao_disc=distribuicao,
            gaps_identificados=analise['gaps'],
            pontos_fortes_time=analise['pontos_fortes'],
            pontos_atencao_time=analise['pontos_atencao'],
            recomendacoes_composicao=analise['recomendacoes']
        )
        
        return comparacao
    
    @staticmethod
    def _calcular_distribuicao(perfis):
        """Calcula distribuição DISC do time"""
        total = len(perfis)
        
        contagem = {'D': 0, 'I': 0, 'S': 0, 'C': 0}
        
        for perfil in perfis:
            contagem[perfil.perfil_principal] += 1
        
        return {
            'D': round((contagem['D'] / total) * 100, 1),
            'I': round((contagem['I'] / total) * 100, 1),
            'S': round((contagem['S'] / total) * 100, 1),
            'C': round((contagem['C'] / total) * 100, 1)
        }
    
    @staticmethod
    def _analisar_composicao(distribuicao):
        """Analisa composição e gera insights"""
        pontos_fortes = []
        pontos_atencao = []
        gaps = []
        recomendacoes = []
        
        # Analisa cada dimensão
        if distribuicao['D'] > 40:
            pontos_fortes.append('Time orientado a resultados e decisões')
            pontos_atencao.append('Possível competição interna excessiva')
        elif distribuicao['D'] < 15:
            gaps.append('Falta de perfil de liderança/decisão')
            recomendacoes.append('Considerar adicionar perfil D ao time')
        
        if distribuicao['I'] > 40:
            pontos_fortes.append('Time comunicativo e entusiasta')
            pontos_atencao.append('Pode faltar foco em detalhes')
        elif distribuicao['I'] < 15:
            gaps.append('Falta de perfil comunicador')
            recomendacoes.append('Considerar adicionar perfil I ao time')
        
        if distribuicao['S'] > 40:
            pontos_fortes.append('Time estável e cooperativo')
            pontos_atencao.append('Pode resistir a mudanças')
        elif distribuicao['S'] < 15:
            gaps.append('Falta de estabilidade no time')
            recomendacoes.append('Considerar adicionar perfil S ao time')
        
        if distribuicao['C'] > 40:
            pontos_fortes.append('Time analítico e preciso')
            pontos_atencao.append('Pode ser lento em decisões')
        elif distribuicao['C'] < 15:
            gaps.append('Falta de perfil analítico')
            recomendacoes.append('Considerar adicionar perfil C ao time')
        
        return {
            'pontos_fortes': pontos_fortes,
            'pontos_atencao': pontos_atencao,
            'gaps': gaps,
            'recomendacoes': recomendacoes
        }
