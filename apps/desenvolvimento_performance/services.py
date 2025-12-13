"""
SyncRH - Desenvolvimento e Performance - Services
=================================================
Camada de serviços com lógica de negócio
"""

from django.db import transaction
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AvaliacaoService:
    """Serviço para gestão de avaliações de desempenho"""
    
    @staticmethod
    @transaction.atomic
    def criar_ciclo_avaliacao(dados):
        """Cria novo ciclo de avaliação"""
        from .models import CicloAvaliacao
        
        ciclo = CicloAvaliacao.objects.create(**dados)
        logger.info(f"Ciclo de avaliação criado: {ciclo.nome}")
        return ciclo
    
    @staticmethod
    def iniciar_ciclo(ciclo):
        """Inicia ciclo de avaliação"""
        from .models import AvaliacaoDesempenho
        from apps.departamento_pessoal.models import Colaborador
        
        # Cria avaliações para todos os colaboradores ativos
        colaboradores = Colaborador.objects.filter(
            status='ativo'
        )
        
        avaliacoes_criadas = []
        
        for colaborador in colaboradores:
            # Autoavaliação
            auto = AvaliacaoDesempenho.objects.create(
                ciclo=ciclo,
                colaborador=colaborador,
                avaliador=colaborador.user,
                tipo='autoavaliacao',
                status='pendente'
            )
            avaliacoes_criadas.append(auto)
            
            # Avaliação do gestor
            if colaborador.gestor:
                gestor = AvaliacaoDesempenho.objects.create(
                    ciclo=ciclo,
                    colaborador=colaborador,
                    avaliador=colaborador.gestor,
                    tipo='gestor',
                    status='pendente'
                )
                avaliacoes_criadas.append(gestor)
        
        ciclo.status = 'em_andamento'
        ciclo.save()
        
        return {
            'ciclo': ciclo,
            'avaliacoes_criadas': len(avaliacoes_criadas)
        }
    
    @staticmethod
    def calcular_nota_final(avaliacao):
        """Calcula nota final da avaliação"""
        from .models import CompetenciaAvaliada
        
        competencias = CompetenciaAvaliada.objects.filter(
            avaliacao=avaliacao
        )
        
        if not competencias.exists():
            return None
        
        # Média ponderada
        soma_ponderada = sum(c.nota * c.peso for c in competencias)
        soma_pesos = sum(c.peso for c in competencias)
        
        if soma_pesos > 0:
            nota = soma_ponderada / soma_pesos
            avaliacao.nota_final = round(nota, 2)
            avaliacao.save()
            return avaliacao.nota_final
        
        return None
    
    @staticmethod
    def finalizar_avaliacao(avaliacao):
        """Finaliza uma avaliação"""
        AvaliacaoService.calcular_nota_final(avaliacao)
        avaliacao.status = 'concluida'
        avaliacao.data_avaliacao = timezone.now()
        avaliacao.save()
        
        # Verifica se deve criar PDI
        if avaliacao.nota_final and avaliacao.nota_final < 3:
            PDIService.criar_pdi_automatico(avaliacao)
        
        return avaliacao


class SyncBoxService:
    """Serviço para gestão da matriz SyncBox (9Box)"""
    
    QUADRANTES = {
        (1, 1): 'baixo_baixo',
        (1, 2): 'baixo_medio',
        (1, 3): 'baixo_alto',
        (2, 1): 'medio_baixo',
        (2, 2): 'medio_medio',
        (2, 3): 'medio_alto',
        (3, 1): 'alto_baixo',
        (3, 2): 'alto_medio',
        (3, 3): 'alto_alto'
    }
    
    @staticmethod
    def classificar_colaborador(colaborador, ciclo):
        """Classifica colaborador na matriz SyncBox"""
        from .models import SyncBox, AvaliacaoDesempenho
        
        # Busca nota de desempenho do ciclo
        avaliacao = AvaliacaoDesempenho.objects.filter(
            colaborador=colaborador,
            ciclo=ciclo,
            tipo='consolidada',
            status='concluida'
        ).first()
        
        if not avaliacao or not avaliacao.nota_final:
            return None
        
        nota_desempenho = float(avaliacao.nota_final)
        
        # Estima potencial (simplificado)
        nota_potencial = SyncBoxService._estimar_potencial(colaborador)
        
        # Determina quadrante
        nivel_desempenho = SyncBoxService._classificar_nivel(nota_desempenho)
        nivel_potencial = SyncBoxService._classificar_nivel(nota_potencial)
        
        quadrante = SyncBoxService.QUADRANTES.get(
            (nivel_desempenho, nivel_potencial),
            'medio_medio'
        )
        
        # Cria ou atualiza registro
        syncbox, created = SyncBox.objects.update_or_create(
            colaborador=colaborador,
            ciclo=ciclo,
            defaults={
                'nota_desempenho': nota_desempenho,
                'nota_potencial': nota_potencial,
                'quadrante': quadrante
            }
        )
        
        return syncbox
    
    @staticmethod
    def _classificar_nivel(nota):
        """Classifica nota em nível (1=baixo, 2=médio, 3=alto)"""
        if nota < 2:
            return 1
        elif nota < 4:
            return 2
        return 3
    
    @staticmethod
    def _estimar_potencial(colaborador):
        """Estima potencial do colaborador"""
        # Implementação simplificada
        # Em produção, consideraria múltiplos fatores
        pontos = 2.5  # Base
        
        # Formação
        if hasattr(colaborador, 'formacao') and colaborador.formacao:
            pontos += 0.5
        
        # Tempo de empresa (estabilidade vs. ambição)
        # Implementação futura
        
        return min(pontos, 5.0)
    
    @staticmethod
    def calibrar_syncbox(syncbox, nova_nota_potencial, justificativa, calibrador):
        """Calibra posição na matriz"""
        syncbox.nota_potencial = nova_nota_potencial
        syncbox.calibrado = True
        syncbox.calibrado_por = calibrador
        syncbox.data_calibracao = timezone.now()
        syncbox.justificativa_calibracao = justificativa
        
        # Recalcula quadrante
        nivel_desempenho = SyncBoxService._classificar_nivel(float(syncbox.nota_desempenho))
        nivel_potencial = SyncBoxService._classificar_nivel(float(nova_nota_potencial))
        
        syncbox.quadrante = SyncBoxService.QUADRANTES.get(
            (nivel_desempenho, nivel_potencial),
            syncbox.quadrante
        )
        
        syncbox.save()
        return syncbox
    
    @staticmethod
    def gerar_recomendacoes(syncbox):
        """Gera recomendações baseadas no quadrante"""
        recomendacoes = {
            'alto_alto': {
                'acao': 'Reter e Promover',
                'desenvolvimento': 'Programas de liderança, mentoria',
                'carreira': 'Candidato a promoção e sucessão'
            },
            'alto_medio': {
                'acao': 'Desenvolver Potencial',
                'desenvolvimento': 'Projetos desafiadores, coaching',
                'carreira': 'Expandir responsabilidades'
            },
            'alto_baixo': {
                'acao': 'Manter Performance',
                'desenvolvimento': 'Reconhecimento, novos desafios',
                'carreira': 'Especialista técnico'
            },
            'medio_alto': {
                'acao': 'Acelerar Desenvolvimento',
                'desenvolvimento': 'Treinamentos técnicos intensivos',
                'carreira': 'Potencial futuro'
            },
            'medio_medio': {
                'acao': 'Acompanhar',
                'desenvolvimento': 'PDI focado, feedback regular',
                'carreira': 'Manutenção na função'
            },
            'medio_baixo': {
                'acao': 'Atenção',
                'desenvolvimento': 'Identificar gaps, suporte próximo',
                'carreira': 'Revisar fit com função'
            },
            'baixo_alto': {
                'acao': 'Investigar',
                'desenvolvimento': 'Coaching, reavaliação de função',
                'carreira': 'Possível realocação'
            },
            'baixo_medio': {
                'acao': 'Plano de Recuperação',
                'desenvolvimento': 'PDI intensivo, acompanhamento',
                'carreira': 'Risco de desligamento'
            },
            'baixo_baixo': {
                'acao': 'Decisão Crítica',
                'desenvolvimento': 'Última chance ou desligamento',
                'carreira': 'Avaliar continuidade'
            }
        }
        
        return recomendacoes.get(syncbox.quadrante, {})


class PDIService:
    """Serviço para gestão de PDIs"""
    
    @staticmethod
    @transaction.atomic
    def criar_pdi(colaborador, gestor, dados):
        """Cria novo PDI"""
        from .models import PDI
        
        pdi = PDI.objects.create(
            colaborador=colaborador,
            gestor=gestor,
            **dados
        )
        
        logger.info(f"PDI criado para {colaborador}: {pdi.titulo}")
        return pdi
    
    @staticmethod
    def criar_pdi_automatico(avaliacao):
        """Cria PDI automaticamente baseado na avaliação"""
        from .models import PDI, AcaoPDI
        
        pdi = PDI.objects.create(
            colaborador=avaliacao.colaborador,
            gestor=avaliacao.avaliador,
            titulo=f'PDI - {avaliacao.ciclo.nome}',
            avaliacao_origem=avaliacao,
            status='pendente',
            data_inicio=timezone.now().date(),
            data_previsao_conclusao=timezone.now().date() + timedelta(days=180)
        )
        
        # Cria ações baseadas nos pontos de melhoria
        if avaliacao.pontos_melhoria:
            AcaoPDI.objects.create(
                pdi=pdi,
                titulo='Desenvolver competências identificadas',
                descricao=avaliacao.pontos_melhoria,
                tipo='capacitacao',
                prioridade='alta',
                status='pendente',
                data_previsao=timezone.now().date() + timedelta(days=90)
            )
        
        return pdi
    
    @staticmethod
    def atualizar_progresso(pdi):
        """Atualiza progresso geral do PDI"""
        from .models import AcaoPDI
        
        acoes = AcaoPDI.objects.filter(pdi=pdi, is_active=True)
        
        if not acoes.exists():
            pdi.progresso_geral = 0
            pdi.save()
            return 0
        
        total = acoes.count()
        soma_progresso = sum(a.progresso or 0 for a in acoes)
        
        pdi.progresso_geral = round(soma_progresso / total)
        
        # Verifica se completou
        if pdi.progresso_geral >= 100:
            pdi.status = 'concluido'
            pdi.data_conclusao = timezone.now().date()
        
        pdi.save()
        return pdi.progresso_geral
    
    @staticmethod
    def verificar_acoes_atrasadas():
        """Verifica e notifica ações atrasadas"""
        from .models import AcaoPDI
        
        hoje = timezone.now().date()
        
        acoes_atrasadas = AcaoPDI.objects.filter(
            status__in=['pendente', 'em_andamento'],
            data_previsao__lt=hoje,
            is_active=True
        )
        
        for acao in acoes_atrasadas:
            acao.status = 'atrasado'
            acao.save()
            
            # Notificar colaborador e gestor
            # Implementação de notificação
        
        return acoes_atrasadas.count()


class LMSService:
    """Serviço para gestão do sistema de aprendizagem (LMS)"""
    
    @staticmethod
    def matricular_colaborador(colaborador, curso, trilha=None):
        """Matricula colaborador em curso"""
        from .models import MatriculaCurso
        
        # Verifica pré-requisitos
        if curso.pre_requisitos:
            # Implementar verificação de pré-requisitos
            pass
        
        matricula, created = MatriculaCurso.objects.get_or_create(
            colaborador=colaborador,
            curso=curso,
            trilha=trilha,
            defaults={
                'status': 'matriculado',
                'data_matricula': timezone.now()
            }
        )
        
        if not created:
            raise ValueError("Colaborador já está matriculado neste curso")
        
        return matricula
    
    @staticmethod
    def registrar_progresso(matricula, modulo, aula, progresso, tempo=None):
        """Registra progresso no curso"""
        from .models import ProgressoCurso
        
        progresso_obj, created = ProgressoCurso.objects.update_or_create(
            matricula=matricula,
            modulo=modulo,
            aula=aula,
            defaults={
                'progresso': progresso,
                'tempo_assistido': tempo,
                'status': 'concluido' if progresso >= 100 else 'em_andamento'
            }
        )
        
        # Atualiza progresso geral da matrícula
        LMSService._atualizar_progresso_matricula(matricula)
        
        return progresso_obj
    
    @staticmethod
    def _atualizar_progresso_matricula(matricula):
        """Atualiza progresso geral da matrícula"""
        from .models import ProgressoCurso
        
        progressos = ProgressoCurso.objects.filter(matricula=matricula)
        
        if progressos.exists():
            media = progressos.aggregate(Avg('progresso'))['progresso__avg']
            matricula.progresso = round(media)
            
            if matricula.progresso >= 100:
                matricula.status = 'concluido'
                matricula.data_conclusao = timezone.now()
            elif matricula.progresso > 0:
                matricula.status = 'em_andamento'
                if not matricula.data_inicio:
                    matricula.data_inicio = timezone.now()
            
            matricula.save()
    
    @staticmethod
    def gerar_certificado(matricula):
        """Gera certificado de conclusão"""
        if matricula.status != 'concluido':
            raise ValueError("Curso não foi concluído")
        
        if matricula.curso.nota_minima and matricula.nota:
            if matricula.nota < matricula.curso.nota_minima:
                raise ValueError("Nota mínima não atingida")
        
        # Gera URL do certificado (implementação simplificada)
        certificado_url = f"/certificados/{matricula.id}/"
        matricula.certificado_url = certificado_url
        matricula.save()
        
        return certificado_url
    
    @staticmethod
    def relatorio_treinamentos(periodo_inicio=None, periodo_fim=None):
        """Gera relatório de treinamentos"""
        from .models import MatriculaCurso, Curso
        
        filtros = {}
        if periodo_inicio:
            filtros['data_matricula__gte'] = periodo_inicio
        if periodo_fim:
            filtros['data_matricula__lte'] = periodo_fim
        
        matriculas = MatriculaCurso.objects.filter(**filtros)
        
        return {
            'total_matriculas': matriculas.count(),
            'concluidas': matriculas.filter(status='concluido').count(),
            'em_andamento': matriculas.filter(status='em_andamento').count(),
            'taxa_conclusao': LMSService._calcular_taxa_conclusao(matriculas),
            'horas_treinamento': LMSService._calcular_horas_treinamento(matriculas),
            'cursos_mais_populares': LMSService._cursos_mais_populares()
        }
    
    @staticmethod
    def _calcular_taxa_conclusao(matriculas):
        """Calcula taxa de conclusão"""
        total = matriculas.count()
        if total == 0:
            return 0
        concluidas = matriculas.filter(status='concluido').count()
        return round((concluidas / total) * 100, 2)
    
    @staticmethod
    def _calcular_horas_treinamento(matriculas):
        """Calcula total de horas de treinamento"""
        from django.db.models import Sum
        
        total = matriculas.filter(
            status='concluido'
        ).aggregate(
            total=Sum('curso__carga_horaria')
        )['total']
        
        return total or 0
    
    @staticmethod
    def _cursos_mais_populares():
        """Retorna cursos mais populares"""
        from .models import Curso
        
        return list(
            Curso.objects.annotate(
                total_matriculas=Count('matriculas')
            ).order_by('-total_matriculas')[:10].values(
                'id', 'titulo', 'total_matriculas'
            )
        )
