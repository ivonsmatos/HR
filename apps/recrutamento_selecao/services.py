"""
SyncRH - Recrutamento e Seleção - Services
==========================================
Camada de serviços com lógica de negócio
"""

from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class VagaService:
    """Serviço para gestão de vagas"""
    
    @staticmethod
    def criar_vaga(data, recrutador):
        """Cria nova vaga com código sequencial"""
        from .models import Vaga
        
        # Gera código sequencial
        ano = timezone.now().year
        ultima_vaga = Vaga.objects.filter(
            codigo__startswith=f'VAG{ano}'
        ).order_by('-codigo').first()
        
        if ultima_vaga:
            numero = int(ultima_vaga.codigo[-4:]) + 1
        else:
            numero = 1
        
        data['codigo'] = f'VAG{ano}{numero:04d}'
        data['recrutador'] = recrutador
        data['data_abertura'] = timezone.now().date()
        
        return Vaga.objects.create(**data)
    
    @staticmethod
    def fechar_vaga(vaga, motivo='preenchida'):
        """Fecha uma vaga"""
        vaga.status = 'fechada'
        vaga.data_fechamento = timezone.now().date()
        vaga.motivo_fechamento = motivo
        vaga.save()
        
        # Notifica candidatos pendentes
        candidaturas_pendentes = vaga.candidaturas.filter(
            status__in=['em_analise', 'entrevista']
        )
        
        for candidatura in candidaturas_pendentes:
            candidatura.status = 'encerrado'
            candidatura.save()
        
        return vaga
    
    @staticmethod
    def calcular_metricas_vaga(vaga):
        """Calcula métricas da vaga"""
        candidaturas = vaga.candidaturas.all()
        
        return {
            'total_candidatos': candidaturas.count(),
            'por_etapa': dict(
                candidaturas.values('etapa_atual').annotate(total=Count('id'))
            ),
            'tempo_medio_etapa': VagaService._calcular_tempo_medio_etapas(candidaturas),
            'taxa_conversao': VagaService._calcular_taxa_conversao(candidaturas),
            'dias_aberta': (timezone.now().date() - vaga.data_abertura).days
        }
    
    @staticmethod
    def _calcular_tempo_medio_etapas(candidaturas):
        """Calcula tempo médio em cada etapa"""
        # Implementação simplificada
        return {}
    
    @staticmethod
    def _calcular_taxa_conversao(candidaturas):
        """Calcula taxa de conversão do funil"""
        total = candidaturas.count()
        if total == 0:
            return 0
        
        contratados = candidaturas.filter(status='contratado').count()
        return round((contratados / total) * 100, 2)


class CandidaturaService:
    """Serviço para gestão de candidaturas"""
    
    @staticmethod
    @transaction.atomic
    def criar_candidatura(vaga, candidato, dados_extra=None):
        """Cria nova candidatura"""
        from .models import Candidatura
        
        # Verifica se já existe candidatura
        existente = Candidatura.objects.filter(
            vaga=vaga,
            candidato=candidato,
            status__in=['em_analise', 'entrevista', 'proposta']
        ).exists()
        
        if existente:
            raise ValueError("Candidato já possui candidatura ativa para esta vaga")
        
        candidatura = Candidatura.objects.create(
            vaga=vaga,
            candidato=candidato,
            status='em_analise',
            etapa_atual='triagem',
            **(dados_extra or {})
        )
        
        # Calcula match de perfil se disponível
        if hasattr(vaga, 'perfil_cargo') and vaga.perfil_cargo:
            candidatura.match_perfil = CandidaturaService._calcular_match(
                candidato, vaga.perfil_cargo
            )
            candidatura.save()
        
        return candidatura
    
    @staticmethod
    def avancar_etapa(candidatura, nova_etapa, observacoes=None):
        """Avança candidatura para próxima etapa"""
        candidatura.etapa_atual = nova_etapa
        candidatura.data_atualizacao = timezone.now()
        
        if observacoes:
            candidatura.observacoes = f"{candidatura.observacoes or ''}\n[{timezone.now().date()}] {observacoes}"
        
        candidatura.save()
        
        # Envia notificação ao candidato
        CandidaturaService._notificar_candidato(candidatura, 'avanco_etapa')
        
        return candidatura
    
    @staticmethod
    def reprovar_candidatura(candidatura, motivo, observacoes=None):
        """Reprova candidatura"""
        candidatura.status = 'reprovado'
        candidatura.motivo_reprovacao = motivo
        candidatura.data_atualizacao = timezone.now()
        candidatura.save()
        
        # Envia email de feedback
        CandidaturaService._notificar_candidato(candidatura, 'reprovacao')
        
        return candidatura
    
    @staticmethod
    def enviar_proposta(candidatura, dados_proposta):
        """Envia proposta ao candidato"""
        candidatura.status = 'proposta'
        candidatura.proposta_enviada = True
        candidatura.data_proposta = timezone.now()
        candidatura.save()
        
        CandidaturaService._notificar_candidato(candidatura, 'proposta')
        
        return candidatura
    
    @staticmethod
    def _calcular_match(candidato, perfil_cargo):
        """Calcula match entre candidato e perfil do cargo"""
        # Lógica simplificada - em produção seria mais complexa
        return 75.0
    
    @staticmethod
    def _notificar_candidato(candidatura, tipo):
        """Envia notificação ao candidato"""
        try:
            templates = {
                'avanco_etapa': {
                    'assunto': f'Atualização da sua candidatura - {candidatura.vaga.titulo}',
                    'mensagem': f'Sua candidatura avançou para a etapa: {candidatura.etapa_atual}'
                },
                'reprovacao': {
                    'assunto': f'Resultado da candidatura - {candidatura.vaga.titulo}',
                    'mensagem': 'Agradecemos seu interesse, mas seguiremos com outros candidatos.'
                },
                'proposta': {
                    'assunto': f'Proposta de trabalho - {candidatura.vaga.titulo}',
                    'mensagem': 'Temos uma proposta para você!'
                }
            }
            
            template = templates.get(tipo, {})
            
            if template and hasattr(settings, 'EMAIL_HOST'):
                send_mail(
                    template['assunto'],
                    template['mensagem'],
                    settings.DEFAULT_FROM_EMAIL,
                    [candidatura.candidato.email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar candidato: {e}")


class EntrevistaService:
    """Serviço para gestão de entrevistas"""
    
    @staticmethod
    def agendar_entrevista(candidatura, dados_entrevista):
        """Agenda nova entrevista"""
        from .models import Entrevista
        
        entrevista = Entrevista.objects.create(
            candidatura=candidatura,
            **dados_entrevista
        )
        
        # Notifica participantes
        EntrevistaService._notificar_participantes(entrevista)
        
        return entrevista
    
    @staticmethod
    def reagendar_entrevista(entrevista, nova_data):
        """Reagenda entrevista"""
        entrevista.data_hora = nova_data
        entrevista.status = 'reagendada'
        entrevista.save()
        
        EntrevistaService._notificar_participantes(entrevista, reagendamento=True)
        
        return entrevista
    
    @staticmethod
    def registrar_parecer(entrevista, parecer, nota, proxima_etapa=None):
        """Registra parecer da entrevista"""
        entrevista.parecer = parecer
        entrevista.nota = nota
        entrevista.status = 'concluida'
        
        if proxima_etapa:
            entrevista.proxima_etapa = proxima_etapa
        
        entrevista.save()
        
        return entrevista
    
    @staticmethod
    def _notificar_participantes(entrevista, reagendamento=False):
        """Notifica participantes da entrevista"""
        try:
            tipo = 'reagendamento' if reagendamento else 'agendamento'
            assunto = f'Entrevista {"reagendada" if reagendamento else "agendada"}: {entrevista.candidatura.vaga.titulo}'
            
            # Notifica candidato
            send_mail(
                assunto,
                f'Data/hora: {entrevista.data_hora}\nLocal: {entrevista.local or entrevista.link_online}',
                settings.DEFAULT_FROM_EMAIL,
                [entrevista.candidatura.candidato.email],
                fail_silently=True
            )
            
            # Notifica entrevistadores
            emails_entrevistadores = list(
                entrevista.entrevistadores.values_list('email', flat=True)
            )
            
            if emails_entrevistadores:
                send_mail(
                    assunto,
                    f'Candidato: {entrevista.candidatura.candidato.nome}\nData/hora: {entrevista.data_hora}',
                    settings.DEFAULT_FROM_EMAIL,
                    emails_entrevistadores,
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar participantes: {e}")


class TriagemService:
    """Serviço para triagem automatizada de candidatos"""
    
    @staticmethod
    def executar_triagem(vaga, criterios=None):
        """Executa triagem automatizada de candidatos"""
        from .models import Candidatura
        
        candidaturas = Candidatura.objects.filter(
            vaga=vaga,
            etapa_atual='triagem'
        )
        
        resultados = {
            'aprovados': [],
            'reprovados': [],
            'pendentes': []
        }
        
        for candidatura in candidaturas:
            score = TriagemService._calcular_score(
                candidatura.candidato, vaga, criterios
            )
            
            if score >= 70:
                candidatura.etapa_atual = 'analise_curricular'
                candidatura.save()
                resultados['aprovados'].append(candidatura.id)
            elif score < 40:
                candidatura.status = 'reprovado'
                candidatura.motivo_reprovacao = 'Não atende aos requisitos mínimos'
                candidatura.save()
                resultados['reprovados'].append(candidatura.id)
            else:
                resultados['pendentes'].append(candidatura.id)
        
        return resultados
    
    @staticmethod
    def _calcular_score(candidato, vaga, criterios):
        """Calcula score de adequação do candidato"""
        # Implementação simplificada
        score = 50  # Base
        
        # Adiciona pontos por experiência
        if candidato.experiencia_profissional:
            score += 15
        
        # Adiciona pontos por formação
        if candidato.formacao_academica:
            score += 15
        
        # Adiciona pontos por habilidades
        if candidato.habilidades:
            score += 10
        
        return min(score, 100)


class RelatorioRecrutamentoService:
    """Serviço para geração de relatórios de recrutamento"""
    
    @staticmethod
    def dashboard_recrutamento():
        """Gera dados para dashboard de recrutamento"""
        from .models import Vaga, Candidatura, Entrevista
        
        hoje = timezone.now().date()
        mes_inicio = hoje.replace(day=1)
        
        return {
            'vagas_abertas': Vaga.objects.filter(status='aberta').count(),
            'vagas_mes': Vaga.objects.filter(
                data_abertura__gte=mes_inicio
            ).count(),
            'candidaturas_mes': Candidatura.objects.filter(
                data_candidatura__gte=mes_inicio
            ).count(),
            'entrevistas_semana': Entrevista.objects.filter(
                data_hora__gte=hoje,
                data_hora__lte=hoje + timedelta(days=7)
            ).count(),
            'contratacoes_mes': Candidatura.objects.filter(
                status='contratado',
                data_atualizacao__gte=mes_inicio
            ).count(),
            'tempo_medio_contratacao': RelatorioRecrutamentoService._tempo_medio_contratacao(),
            'taxa_conversao_geral': RelatorioRecrutamentoService._taxa_conversao_geral(),
            'fontes_candidatos': RelatorioRecrutamentoService._fontes_candidatos()
        }
    
    @staticmethod
    def _tempo_medio_contratacao():
        """Calcula tempo médio de contratação"""
        from .models import Candidatura
        from django.db.models import F, Avg
        
        # Simplificado - retorna em dias
        return 30
    
    @staticmethod
    def _taxa_conversao_geral():
        """Calcula taxa de conversão geral"""
        from .models import Candidatura
        
        total = Candidatura.objects.count()
        if total == 0:
            return 0
        
        contratados = Candidatura.objects.filter(status='contratado').count()
        return round((contratados / total) * 100, 2)
    
    @staticmethod
    def _fontes_candidatos():
        """Retorna distribuição de fontes de candidatos"""
        from .models import Candidato
        
        return list(
            Candidato.objects.values('origem').annotate(
                total=Count('id')
            ).order_by('-total')[:10]
        )
