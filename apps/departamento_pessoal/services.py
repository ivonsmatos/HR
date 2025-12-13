"""
SyncRH - Departamento Pessoal - Services
========================================

Camada de serviços com regras de negócio do módulo Departamento Pessoal.
Separa a lógica de negócio das views para melhor organização e testabilidade.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    Colaborador, RegistroPonto, JustificativaPonto,
    FolhaPagamento, ItemFolha, PeriodoAquisitivo,
    SolicitacaoFerias, DocumentoGED
)


class PontoService:
    """
    Serviço para gerenciamento de ponto eletrônico.
    
    Responsabilidades:
    - Registrar batidas de ponto
    - Calcular horas trabalhadas
    - Gerar espelho de ponto
    - Processar justificativas
    """
    
    def registrar_ponto(
        self,
        colaborador: Colaborador,
        origem: str = 'web',
        localizacao: Optional[Dict] = None,
        observacao: str = ''
    ) -> Dict[str, Any]:
        """
        Registra batida de ponto do colaborador.
        
        Args:
            colaborador: Colaborador que está registrando
            origem: Origem do registro (web, app, facial, etc)
            localizacao: Coordenadas GPS (opcional)
            observacao: Observação do registro
            
        Returns:
            Dict com dados do registro criado
        """
        agora = timezone.now()
        hoje = agora.date()
        
        # Busca último registro do dia
        ultimo_registro = RegistroPonto.objects.filter(
            colaborador=colaborador,
            data=hoje
        ).order_by('-hora').first()
        
        # Determina o tipo do registro
        if not ultimo_registro:
            tipo = 'entrada'
        elif ultimo_registro.tipo == 'entrada':
            tipo = 'inicio_intervalo'
        elif ultimo_registro.tipo == 'inicio_intervalo':
            tipo = 'fim_intervalo'
        elif ultimo_registro.tipo == 'fim_intervalo':
            tipo = 'saida'
        else:
            tipo = 'entrada'  # Novo ciclo
        
        # Cria o registro
        registro = RegistroPonto.objects.create(
            colaborador=colaborador,
            data=hoje,
            hora=agora.time(),
            tipo=tipo,
            origem=origem,
            localizacao=localizacao or {},
            observacao=observacao
        )
        
        return {
            'id': registro.id,
            'uuid': str(registro.uuid),
            'tipo': registro.tipo,
            'hora': registro.hora.strftime('%H:%M:%S'),
            'mensagem': f'Ponto de {tipo} registrado com sucesso!'
        }
    
    def gerar_espelho(
        self,
        colaborador: Colaborador,
        mes: int,
        ano: int
    ) -> Dict[str, Any]:
        """
        Gera espelho de ponto do colaborador.
        
        Args:
            colaborador: Colaborador
            mes: Mês de referência
            ano: Ano de referência
            
        Returns:
            Dict com espelho de ponto
        """
        # Busca registros do mês
        registros = RegistroPonto.objects.filter(
            colaborador=colaborador,
            data__month=mes,
            data__year=ano
        ).order_by('data', 'hora')
        
        # Agrupa por dia
        dias = {}
        for registro in registros:
            dia = registro.data.strftime('%Y-%m-%d')
            if dia not in dias:
                dias[dia] = []
            dias[dia].append({
                'hora': registro.hora.strftime('%H:%M'),
                'tipo': registro.tipo,
                'origem': registro.origem
            })
        
        # Calcula totais
        total_horas = timedelta()
        for dia, batidas in dias.items():
            horas_dia = self._calcular_horas_dia(batidas)
            total_horas += horas_dia
        
        return {
            'colaborador': colaborador.nome_completo,
            'mes': mes,
            'ano': ano,
            'dias': dias,
            'total_dias': len(dias),
            'total_horas': str(total_horas),
            'gerado_em': timezone.now().isoformat()
        }
    
    def _calcular_horas_dia(self, batidas: List[Dict]) -> timedelta:
        """Calcula horas trabalhadas em um dia"""
        total = timedelta()
        entrada = None
        
        for batida in batidas:
            hora = datetime.strptime(batida['hora'], '%H:%M').time()
            
            if batida['tipo'] in ['entrada', 'fim_intervalo']:
                entrada = hora
            elif batida['tipo'] in ['saida', 'inicio_intervalo'] and entrada:
                # Calcula diferença
                entrada_dt = datetime.combine(date.today(), entrada)
                saida_dt = datetime.combine(date.today(), hora)
                total += saida_dt - entrada_dt
                entrada = None
        
        return total


class FeriasService:
    """
    Serviço para gerenciamento de férias.
    
    Responsabilidades:
    - Calcular períodos aquisitivos
    - Processar solicitações
    - Aprovar/rejeitar férias
    - Calcular valores
    """
    
    def calcular_periodo_aquisitivo(
        self,
        colaborador: Colaborador
    ) -> Optional[PeriodoAquisitivo]:
        """
        Calcula/atualiza período aquisitivo do colaborador.
        
        Args:
            colaborador: Colaborador
            
        Returns:
            PeriodoAquisitivo atualizado ou None
        """
        hoje = date.today()
        admissao = colaborador.data_admissao
        
        # Calcula anos completos
        anos = (hoje - admissao).days // 365
        
        if anos < 1:
            return None
        
        # Busca ou cria período
        periodo_inicio = admissao + timedelta(days=365 * (anos - 1))
        periodo_fim = admissao + timedelta(days=365 * anos - 1)
        
        periodo, created = PeriodoAquisitivo.objects.get_or_create(
            colaborador=colaborador,
            data_inicio=periodo_inicio,
            defaults={
                'data_fim': periodo_fim,
                'dias_direito': 30
            }
        )
        
        return periodo
    
    @transaction.atomic
    def aprovar(
        self,
        solicitacao: SolicitacaoFerias,
        aprovador
    ) -> Dict[str, Any]:
        """
        Aprova solicitação de férias.
        
        Args:
            solicitacao: Solicitação a aprovar
            aprovador: Usuário que está aprovando
            
        Returns:
            Dict com resultado
        """
        if solicitacao.status not in ['pendente', 'aprovado_gestor']:
            raise ValidationError('Solicitação não pode ser aprovada neste status.')
        
        solicitacao.status = 'aprovado'
        solicitacao.aprovado_por = aprovador
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        # Atualiza período aquisitivo
        if solicitacao.periodo_aquisitivo:
            periodo = solicitacao.periodo_aquisitivo
            periodo.dias_gozados += solicitacao.dias_solicitados
            if solicitacao.abono_pecuniario:
                periodo.dias_vendidos += solicitacao.dias_abono
            periodo.save()
        
        return {
            'status': 'aprovado',
            'mensagem': 'Férias aprovadas com sucesso!',
            'solicitacao_id': solicitacao.id
        }
    
    @transaction.atomic
    def rejeitar(
        self,
        solicitacao: SolicitacaoFerias,
        aprovador,
        motivo: str
    ) -> Dict[str, Any]:
        """
        Rejeita solicitação de férias.
        
        Args:
            solicitacao: Solicitação a rejeitar
            aprovador: Usuário que está rejeitando
            motivo: Motivo da rejeição
            
        Returns:
            Dict com resultado
        """
        if solicitacao.status not in ['pendente', 'aprovado_gestor']:
            raise ValidationError('Solicitação não pode ser rejeitada neste status.')
        
        solicitacao.status = 'rejeitado'
        solicitacao.aprovado_por = aprovador
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.observacoes = f'{solicitacao.observacoes}\n\nMotivo rejeição: {motivo}'
        solicitacao.save()
        
        return {
            'status': 'rejeitado',
            'mensagem': 'Férias rejeitadas.',
            'motivo': motivo,
            'solicitacao_id': solicitacao.id
        }
    
    def calcular_valor_ferias(
        self,
        colaborador: Colaborador,
        dias: int,
        com_abono: bool = False,
        dias_abono: int = 0
    ) -> Dict[str, Decimal]:
        """
        Calcula valores de férias.
        
        Args:
            colaborador: Colaborador
            dias: Dias de férias
            com_abono: Se tem abono pecuniário
            dias_abono: Dias de abono
            
        Returns:
            Dict com valores calculados
        """
        salario = colaborador.cargo.salario_base if colaborador.cargo else Decimal('0')
        
        valor_dia = salario / 30
        valor_ferias = valor_dia * dias
        terco_constitucional = valor_ferias / 3
        
        valor_abono = Decimal('0')
        if com_abono and dias_abono > 0:
            valor_abono = (valor_dia * dias_abono) + (valor_dia * dias_abono / 3)
        
        total_bruto = valor_ferias + terco_constitucional + valor_abono
        
        return {
            'salario_base': salario,
            'valor_dia': valor_dia,
            'valor_ferias': valor_ferias,
            'terco_constitucional': terco_constitucional,
            'valor_abono': valor_abono,
            'total_bruto': total_bruto
        }


class FolhaPagamentoService:
    """
    Serviço para processamento de folha de pagamento.
    
    Responsabilidades:
    - Calcular proventos e descontos
    - Gerar folha de pagamento
    - Processar adiantamentos
    - Integração contábil
    """
    
    @transaction.atomic
    def processar_folha(
        self,
        colaborador: Colaborador,
        mes: int,
        ano: int
    ) -> FolhaPagamento:
        """
        Processa folha de pagamento do colaborador.
        
        Args:
            colaborador: Colaborador
            mes: Mês de referência
            ano: Ano de referência
            
        Returns:
            FolhaPagamento processada
        """
        # Busca ou cria folha
        folha, created = FolhaPagamento.objects.get_or_create(
            colaborador=colaborador,
            mes=mes,
            ano=ano,
            defaults={
                'salario_base': colaborador.cargo.salario_base if colaborador.cargo else Decimal('0')
            }
        )
        
        if folha.status == 'fechada':
            raise ValidationError('Folha já está fechada.')
        
        # Limpa itens existentes
        folha.itens.all().delete()
        
        # Adiciona salário base
        ItemFolha.objects.create(
            folha=folha,
            codigo='001',
            descricao='Salário Base',
            tipo='provento',
            valor=folha.salario_base
        )
        
        # Calcula descontos
        self._calcular_inss(folha)
        self._calcular_irrf(folha)
        
        # Atualiza totais
        folha.total_proventos = sum(
            item.valor for item in folha.itens.filter(tipo='provento')
        )
        folha.total_descontos = sum(
            item.valor for item in folha.itens.filter(tipo='desconto')
        )
        folha.salario_liquido = folha.total_proventos - folha.total_descontos
        folha.status = 'processada'
        folha.save()
        
        return folha
    
    def _calcular_inss(self, folha: FolhaPagamento) -> None:
        """Calcula desconto de INSS"""
        # Tabela INSS 2024 (simplificada)
        salario = folha.salario_base
        
        if salario <= Decimal('1412.00'):
            aliquota = Decimal('0.075')
        elif salario <= Decimal('2666.68'):
            aliquota = Decimal('0.09')
        elif salario <= Decimal('4000.03'):
            aliquota = Decimal('0.12')
        elif salario <= Decimal('7786.02'):
            aliquota = Decimal('0.14')
        else:
            aliquota = Decimal('0.14')
            salario = Decimal('7786.02')  # Teto
        
        valor_inss = salario * aliquota
        
        ItemFolha.objects.create(
            folha=folha,
            codigo='101',
            descricao='INSS',
            tipo='desconto',
            referencia=f'{aliquota * 100}%',
            valor=valor_inss
        )
    
    def _calcular_irrf(self, folha: FolhaPagamento) -> None:
        """Calcula desconto de IRRF"""
        # Base de cálculo (salário - INSS)
        inss = folha.itens.filter(codigo='101').first()
        base = folha.salario_base - (inss.valor if inss else Decimal('0'))
        
        # Tabela IRRF 2024 (simplificada)
        if base <= Decimal('2259.20'):
            return  # Isento
        elif base <= Decimal('2826.65'):
            aliquota = Decimal('0.075')
            deducao = Decimal('169.44')
        elif base <= Decimal('3751.05'):
            aliquota = Decimal('0.15')
            deducao = Decimal('381.44')
        elif base <= Decimal('4664.68'):
            aliquota = Decimal('0.225')
            deducao = Decimal('662.77')
        else:
            aliquota = Decimal('0.275')
            deducao = Decimal('896.00')
        
        valor_irrf = (base * aliquota) - deducao
        
        if valor_irrf > 0:
            ItemFolha.objects.create(
                folha=folha,
                codigo='102',
                descricao='IRRF',
                tipo='desconto',
                referencia=f'{aliquota * 100}%',
                valor=valor_irrf
            )


class DocumentoService:
    """
    Serviço para gerenciamento de documentos (GED).
    
    Responsabilidades:
    - Upload e validação de documentos
    - Controle de vencimento
    - Notificações de documentos vencidos
    """
    
    def verificar_documentos_vencidos(self) -> List[DocumentoGED]:
        """
        Retorna lista de documentos vencidos ou próximos do vencimento.
        
        Returns:
            Lista de DocumentoGED
        """
        hoje = date.today()
        limite = hoje + timedelta(days=30)  # 30 dias para vencer
        
        return DocumentoGED.objects.filter(
            is_active=True,
            data_validade__lte=limite
        ).select_related('colaborador', 'categoria')
    
    def documentos_pendentes_colaborador(
        self,
        colaborador: Colaborador
    ) -> Dict[str, List]:
        """
        Lista documentos pendentes de um colaborador.
        
        Args:
            colaborador: Colaborador
            
        Returns:
            Dict com documentos faltantes e vencidos
        """
        from .models import CategoriaDocumento
        
        # Categorias obrigatórias
        categorias_obrigatorias = CategoriaDocumento.objects.filter(obrigatorio=True)
        
        # Documentos do colaborador
        docs_colaborador = DocumentoGED.objects.filter(
            colaborador=colaborador,
            is_active=True
        ).values_list('categoria_id', flat=True)
        
        # Faltantes
        faltantes = categorias_obrigatorias.exclude(id__in=docs_colaborador)
        
        # Vencidos
        hoje = date.today()
        vencidos = DocumentoGED.objects.filter(
            colaborador=colaborador,
            is_active=True,
            data_validade__lt=hoje
        )
        
        return {
            'faltantes': list(faltantes.values('id', 'nome')),
            'vencidos': list(vencidos.values('id', 'titulo', 'data_validade'))
        }
