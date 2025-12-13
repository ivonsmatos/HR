"""
SyncRH - Serviços NIST
======================
Serviços para operações do framework NIST CSF
"""

from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import logging
import json

logger = logging.getLogger(__name__)


class AvaliacaoRiscoService:
    """
    Serviço para avaliação e gestão de riscos conforme NIST.
    """
    
    # Matriz de Risco 5x5
    MATRIZ_RISCO = {
        (5, 5): {'nivel': 'critico', 'score': 25},
        (5, 4): {'nivel': 'critico', 'score': 20},
        (4, 5): {'nivel': 'critico', 'score': 20},
        (5, 3): {'nivel': 'alto', 'score': 15},
        (3, 5): {'nivel': 'alto', 'score': 15},
        (4, 4): {'nivel': 'alto', 'score': 16},
        (5, 2): {'nivel': 'medio', 'score': 10},
        (2, 5): {'nivel': 'medio', 'score': 10},
        (4, 3): {'nivel': 'alto', 'score': 12},
        (3, 4): {'nivel': 'alto', 'score': 12},
        (5, 1): {'nivel': 'baixo', 'score': 5},
        (1, 5): {'nivel': 'baixo', 'score': 5},
    }
    
    @staticmethod
    def calcular_nivel_risco(probabilidade: int, impacto: int) -> dict:
        """
        Calcula nível de risco baseado na matriz 5x5.
        
        Probabilidade e Impacto: 1-5
        Score = Probabilidade x Impacto
        
        1-4: muito_baixo
        5-8: baixo
        9-12: medio
        13-19: alto
        20-25: critico
        """
        score = probabilidade * impacto
        
        if score <= 4:
            nivel = 'muito_baixo'
        elif score <= 8:
            nivel = 'baixo'
        elif score <= 12:
            nivel = 'medio'
        elif score <= 19:
            nivel = 'alto'
        else:
            nivel = 'critico'
        
        return {
            'score': score,
            'nivel': nivel,
            'probabilidade': probabilidade,
            'impacto': impacto,
        }
    
    @staticmethod
    @transaction.atomic
    def criar_avaliacao(dados, avaliador):
        """Cria nova avaliação de risco"""
        from .models import AvaliacaoRisco
        
        calculo = AvaliacaoRiscoService.calcular_nivel_risco(
            dados.get('probabilidade', 1),
            dados.get('impacto', 1)
        )
        
        avaliacao = AvaliacaoRisco.objects.create(
            avaliador=avaliador,
            score_risco=calculo['score'],
            nivel_risco=calculo['nivel'],
            **dados
        )
        
        # Se risco alto/crítico, notifica responsáveis
        if calculo['nivel'] in ['alto', 'critico']:
            AvaliacaoRiscoService._notificar_risco_alto(avaliacao)
        
        return avaliacao
    
    @staticmethod
    def _notificar_risco_alto(avaliacao):
        """Notifica sobre risco alto ou crítico"""
        try:
            security_email = getattr(settings, 'SECURITY_TEAM_EMAIL', None)
            if security_email:
                send_mail(
                    f'[ALERTA] Risco {avaliacao.nivel_risco.upper()} Identificado',
                    f'Nova avaliação de risco com nível {avaliacao.nivel_risco}.\n'
                    f'Ativo: {avaliacao.ativo}\n'
                    f'Ameaça: {avaliacao.ameaca}\n'
                    f'Score: {avaliacao.score_risco}/25\n',
                    settings.DEFAULT_FROM_EMAIL,
                    [security_email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar risco alto: {e}")


class DeteccaoService:
    """
    Serviço para detecção de ameaças e anomalias.
    """
    
    @staticmethod
    def processar_evento(tipo_evento: str, dados: dict, origem: str):
        """
        Processa evento e verifica contra regras de detecção.
        """
        from .models import RegraDeteccao, AlertaSeguranca
        
        # Busca regras ativas
        regras = RegraDeteccao.objects.filter(
            ativa=True,
            tipo_evento=tipo_evento
        )
        
        alertas_gerados = []
        
        for regra in regras:
            if DeteccaoService._verificar_regra(regra, dados):
                alerta = AlertaSeguranca.objects.create(
                    regra=regra,
                    titulo=f'Alerta: {regra.nome}',
                    descricao=regra.descricao,
                    severidade=regra.severidade,
                    dados_evento=dados,
                    origem=origem
                )
                alertas_gerados.append(alerta)
                
                # Notifica se severidade alta
                if regra.severidade in ['alta', 'critica']:
                    DeteccaoService._notificar_alerta(alerta)
        
        return alertas_gerados
    
    @staticmethod
    def _verificar_regra(regra, dados: dict) -> bool:
        """
        Verifica se os dados correspondem às condições da regra.
        Suporta operadores: equals, contains, greater_than, less_than, in, regex
        """
        try:
            condicoes = regra.condicoes
            if not condicoes:
                return False
            
            for campo, config in condicoes.items():
                valor_dado = dados.get(campo)
                if valor_dado is None:
                    return False
                
                operador = config.get('operador', 'equals')
                valor_regra = config.get('valor')
                
                if operador == 'equals' and valor_dado != valor_regra:
                    return False
                elif operador == 'contains' and valor_regra not in str(valor_dado):
                    return False
                elif operador == 'greater_than' and float(valor_dado) <= float(valor_regra):
                    return False
                elif operador == 'less_than' and float(valor_dado) >= float(valor_regra):
                    return False
                elif operador == 'in' and valor_dado not in valor_regra:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar regra {regra.id}: {e}")
            return False
    
    @staticmethod
    def _notificar_alerta(alerta):
        """Notifica sobre alerta de segurança"""
        try:
            security_email = getattr(settings, 'SECURITY_TEAM_EMAIL', None)
            if security_email:
                send_mail(
                    f'[SEGURANÇA] Alerta {alerta.severidade.upper()}: {alerta.titulo}',
                    f'{alerta.descricao}\n\nOrigem: {alerta.origem}\n'
                    f'Data: {alerta.created_at}',
                    settings.DEFAULT_FROM_EMAIL,
                    [security_email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar alerta: {e}")


class IncidenteResponseService:
    """
    Serviço para resposta a incidentes conforme NIST.
    """
    
    @staticmethod
    @transaction.atomic
    def iniciar_resposta(plano, incidente, iniciado_por):
        """Inicia execução de plano de resposta a incidente"""
        from .models import AcaoResposta
        
        plano.status = 'em_execucao'
        plano.data_ultima_execucao = timezone.now()
        plano.save()
        
        # Cria ações baseadas nas ações predefinidas do plano
        acoes_criadas = []
        for idx, acao_def in enumerate(plano.acoes_predefinidas):
            acao = AcaoResposta.objects.create(
                incidente=incidente,
                plano=plano,
                tipo_acao=acao_def.get('tipo', 'investigacao'),
                titulo=acao_def.get('titulo', f'Ação {idx + 1}'),
                descricao=acao_def.get('descricao', ''),
                prioridade=acao_def.get('prioridade', 'media'),
                status='pendente'
            )
            acoes_criadas.append(acao)
        
        logger.info(f"Plano de resposta {plano.id} iniciado com {len(acoes_criadas)} ações")
        return acoes_criadas
    
    @staticmethod
    def executar_acao(acao, executada_por, resultado=''):
        """Marca ação como executada"""
        acao.status = 'em_andamento'
        acao.responsavel = executada_por
        acao.data_inicio = timezone.now()
        acao.save()
        
        return acao
    
    @staticmethod
    def concluir_acao(acao, resultado, efetiva=True):
        """Conclui ação de resposta"""
        acao.status = 'concluida'
        acao.resultado = resultado
        acao.efetiva = efetiva
        acao.data_conclusao = timezone.now()
        acao.save()
        
        return acao


class RecuperacaoService:
    """
    Serviço para recuperação de desastres.
    """
    
    @staticmethod
    @transaction.atomic
    def iniciar_recuperacao(plano, tipo_desastre, iniciado_por):
        """Inicia execução de plano de recuperação"""
        plano.status = 'em_execucao'
        plano.data_ultima_execucao = timezone.now()
        plano.save()
        
        logger.info(f"Plano de recuperação {plano.nome} iniciado - {tipo_desastre}")
        
        # Notifica equipe
        RecuperacaoService._notificar_inicio_recuperacao(plano, tipo_desastre)
        
        return plano
    
    @staticmethod
    def registrar_teste(plano, testado_por, cenario, resultado, observacoes=''):
        """Registra teste de plano de recuperação"""
        from .models import TesteRecuperacao
        
        teste = TesteRecuperacao.objects.create(
            plano=plano,
            testado_por=testado_por,
            cenario=cenario,
            resultado=resultado,
            observacoes=observacoes
        )
        
        return teste
    
    @staticmethod
    def registrar_backup(dados, executado_por=None):
        """Registra backup realizado"""
        from .models import BackupRegistro
        
        backup = BackupRegistro.objects.create(
            executado_por=executado_por,
            **dados
        )
        
        return backup
    
    @staticmethod
    def verificar_backup(backup, verificado_por, integridade_ok, checksum_verificado=None):
        """Verifica integridade de backup"""
        backup.verificado = True
        backup.data_verificacao = timezone.now()
        backup.integridade_ok = integridade_ok
        backup.verificado_por = verificado_por
        if checksum_verificado:
            backup.checksum_verificado = checksum_verificado
        backup.save()
        
        return backup
    
    @staticmethod
    def _notificar_inicio_recuperacao(plano, tipo_desastre):
        """Notifica equipe sobre início de recuperação"""
        try:
            it_team_email = getattr(settings, 'IT_TEAM_EMAIL', None)
            if it_team_email:
                send_mail(
                    f'[URGENTE] Plano de Recuperação Ativado: {plano.nome}',
                    f'O plano de recuperação foi ativado.\n\n'
                    f'Plano: {plano.nome}\n'
                    f'Tipo de Desastre: {tipo_desastre}\n'
                    f'RTO: {plano.rto_horas} horas\n'
                    f'RPO: {plano.rpo_horas} horas\n',
                    settings.DEFAULT_FROM_EMAIL,
                    [it_team_email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar recuperação: {e}")


class ConfiguracaoSegurancaService:
    """
    Serviço para gestão de configurações de segurança.
    """
    
    @staticmethod
    def verificar_conformidade(configuracao):
        """
        Verifica conformidade de configuração contra baseline.
        """
        if not configuracao.baseline:
            return {'conforme': False, 'motivo': 'Baseline não definido'}
        
        nao_conformidades = []
        
        for chave, valor_baseline in configuracao.baseline.items():
            valor_atual = configuracao.configuracao_atual.get(chave)
            
            if valor_atual is None:
                nao_conformidades.append({
                    'chave': chave,
                    'esperado': valor_baseline,
                    'atual': 'não definido'
                })
            elif valor_atual != valor_baseline:
                nao_conformidades.append({
                    'chave': chave,
                    'esperado': valor_baseline,
                    'atual': valor_atual
                })
        
        return {
            'conforme': len(nao_conformidades) == 0,
            'nao_conformidades': nao_conformidades,
            'percentual_conformidade': (
                (len(configuracao.baseline) - len(nao_conformidades)) / 
                len(configuracao.baseline) * 100
            ) if configuracao.baseline else 0
        }
    
    @staticmethod
    def aplicar_baseline(configuracao, aplicado_por):
        """Aplica baseline de segurança à configuração atual"""
        desvios_anteriores = []
        
        for chave, valor_baseline in configuracao.baseline.items():
            valor_atual = configuracao.configuracao_atual.get(chave)
            if valor_atual != valor_baseline:
                desvios_anteriores.append({
                    'chave': chave,
                    'valor_anterior': valor_atual,
                    'valor_novo': valor_baseline
                })
                configuracao.configuracao_atual[chave] = valor_baseline
        
        configuracao.em_conformidade = True
        configuracao.ultima_verificacao = timezone.now()
        configuracao.save()
        
        logger.info(
            f"Baseline aplicado à configuração {configuracao.sistema} "
            f"por {aplicado_por} - {len(desvios_anteriores)} ajustes"
        )
        
        return desvios_anteriores


class TreinamentoService:
    """
    Serviço para gestão de treinamentos de segurança.
    """
    
    @staticmethod
    def registrar_conclusao(treinamento, participante, nota=None, certificado_url=None):
        """Registra conclusão de treinamento por participante"""
        from .models import TreinamentoSeguranca
        
        # Atualiza participante
        participantes = treinamento.participantes or []
        
        registro = {
            'usuario_id': participante.id,
            'username': participante.username,
            'data_conclusao': timezone.now().isoformat(),
            'nota': nota,
            'certificado_url': certificado_url
        }
        
        # Remove registro anterior se existir
        participantes = [p for p in participantes if p.get('usuario_id') != participante.id]
        participantes.append(registro)
        
        treinamento.participantes = participantes
        treinamento.save()
        
        return registro
    
    @staticmethod
    def verificar_treinamentos_pendentes(usuario):
        """Verifica treinamentos obrigatórios pendentes para usuário"""
        from .models import TreinamentoSeguranca
        
        treinamentos_obrigatorios = TreinamentoSeguranca.objects.filter(
            obrigatorio=True,
            status='ativo',
            data_validade__gte=timezone.now().date()
        )
        
        pendentes = []
        for treinamento in treinamentos_obrigatorios:
            participantes = treinamento.participantes or []
            concluiu = any(p.get('usuario_id') == usuario.id for p in participantes)
            
            if not concluiu:
                pendentes.append(treinamento)
        
        return pendentes
