"""
SyncRH - Permissões Customizadas
================================
Classes de permissão para controle de acesso granular
"""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acesso ao proprietário do objeto ou administradores.
    
    O objeto deve ter um campo 'user' ou 'created_by' que referencia o usuário.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admins têm acesso total
        if request.user.is_staff:
            return True
        
        # Verifica se é o proprietário
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        if hasattr(obj, 'colaborador'):
            colaborador = obj.colaborador
            if hasattr(colaborador, 'user'):
                return colaborador.user == request.user
        
        return False


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permite acesso a gestores do departamento ou administradores.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Verifica se é gestor
        return self._is_manager(request.user)
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Verifica se é gestor do departamento do objeto
        if hasattr(obj, 'departamento'):
            return self._manages_department(request.user, obj.departamento)
        
        if hasattr(obj, 'colaborador') and hasattr(obj.colaborador, 'departamento'):
            return self._manages_department(request.user, obj.colaborador.departamento)
        
        return False
    
    def _is_manager(self, user):
        """Verifica se o usuário é gestor de algum departamento"""
        if hasattr(user, 'colaborador'):
            colaborador = user.colaborador
            if hasattr(colaborador, 'is_gestor'):
                return colaborador.is_gestor
        return False
    
    def _manages_department(self, user, departamento):
        """Verifica se o usuário é gestor do departamento"""
        if hasattr(departamento, 'gestor'):
            return departamento.gestor == user
        return False


class IsHROrAdmin(permissions.BasePermission):
    """
    Permite acesso apenas a membros do RH ou administradores.
    """
    
    HR_GROUP_NAME = 'RH'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Verifica se pertence ao grupo RH
        return request.user.groups.filter(name=self.HR_GROUP_NAME).exists()


class IsFinanceOrAdmin(permissions.BasePermission):
    """
    Permite acesso apenas a membros do Financeiro ou administradores.
    """
    
    FINANCE_GROUP_NAME = 'Financeiro'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        return request.user.groups.filter(name=self.FINANCE_GROUP_NAME).exists()


class IsSameCompany(permissions.BasePermission):
    """
    Permite acesso apenas a objetos da mesma empresa (multi-tenant).
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superusers têm acesso global
        if request.user.is_superuser:
            return True
        
        # Verifica se o objeto pertence à mesma empresa
        user_company = self._get_user_company(request.user)
        obj_company = self._get_obj_company(obj)
        
        if user_company and obj_company:
            return user_company == obj_company
        
        return True  # Se não houver empresa definida, permite
    
    def _get_user_company(self, user):
        """Obtém a empresa do usuário"""
        if hasattr(user, 'company'):
            return user.company
        if hasattr(user, 'colaborador') and hasattr(user.colaborador, 'empresa'):
            return user.colaborador.empresa
        return None
    
    def _get_obj_company(self, obj):
        """Obtém a empresa do objeto"""
        if hasattr(obj, 'empresa'):
            return obj.empresa
        if hasattr(obj, 'company'):
            return obj.company
        return None


class ReadOnly(permissions.BasePermission):
    """
    Permite apenas operações de leitura (GET, HEAD, OPTIONS).
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permite leitura para todos, escrita apenas para autenticados.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class DepartmentBasedPermission(permissions.BasePermission):
    """
    Permissão baseada em departamento.
    
    Permite acesso baseado no departamento do usuário:
    - Usuários podem ver dados do próprio departamento
    - Gestores podem editar dados do departamento
    - RH pode ver todos os departamentos
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admins e RH têm acesso total
        if user.is_staff or user.groups.filter(name='RH').exists():
            return True
        
        # Obtém departamento do usuário
        user_dept = self._get_user_department(user)
        obj_dept = self._get_obj_department(obj)
        
        if not user_dept or not obj_dept:
            return False
        
        # Mesmo departamento
        if user_dept == obj_dept:
            # Leitura permitida para todos do departamento
            if request.method in permissions.SAFE_METHODS:
                return True
            # Escrita apenas para gestores
            return self._is_department_manager(user, user_dept)
        
        return False
    
    def _get_user_department(self, user):
        if hasattr(user, 'colaborador') and hasattr(user.colaborador, 'departamento'):
            return user.colaborador.departamento
        return None
    
    def _get_obj_department(self, obj):
        if hasattr(obj, 'departamento'):
            return obj.departamento
        if hasattr(obj, 'colaborador') and hasattr(obj.colaborador, 'departamento'):
            return obj.colaborador.departamento
        return None
    
    def _is_department_manager(self, user, department):
        if hasattr(department, 'gestor'):
            return department.gestor == user
        return False


class ActionBasedPermission(permissions.BasePermission):
    """
    Permissão baseada na ação do ViewSet.
    
    Uso no ViewSet:
        permission_classes_by_action = {
            'list': [IsAuthenticated],
            'create': [IsHROrAdmin],
            'update': [IsOwnerOrAdmin],
            'destroy': [IsAdminUser],
        }
    """
    
    def has_permission(self, request, view):
        if not hasattr(view, 'permission_classes_by_action'):
            return True
        
        action = getattr(view, 'action', None)
        if not action:
            return True
        
        permission_classes = view.permission_classes_by_action.get(action, [])
        
        for permission_class in permission_classes:
            permission = permission_class()
            if not permission.has_permission(request, view):
                return False
        
        return True


# Combinações comuns de permissões
class IsOwnerOrHROrAdmin(permissions.BasePermission):
    """Permite acesso ao proprietário, RH ou administradores."""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.is_staff:
            return True
        
        if user.groups.filter(name='RH').exists():
            return True
        
        # Verifica proprietário
        if hasattr(obj, 'user') and obj.user == user:
            return True
        
        if hasattr(obj, 'colaborador'):
            if hasattr(obj.colaborador, 'user') and obj.colaborador.user == user:
                return True
        
        return False


class IsManagerOrHROrAdmin(permissions.BasePermission):
    """Permite acesso ao gestor direto, RH ou administradores."""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.is_staff:
            return True
        
        if user.groups.filter(name='RH').exists():
            return True
        
        # Verifica se é gestor do colaborador
        if hasattr(obj, 'colaborador') and hasattr(obj.colaborador, 'gestor'):
            return obj.colaborador.gestor == user
        
        if hasattr(obj, 'gestor'):
            return obj.gestor == user
        
        return False
