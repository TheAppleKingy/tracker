from infra.exc import ServiceError


class TaskServiceError(ServiceError):
    layer_instance_class_name = 'TaskService'


class UserServiceError(ServiceError):
    layer_instance_class_name = 'UserService'


class UserPermissionServiceError(ServiceError):
    layer_instance_class_name = 'UserPermissionService'


class UserAuthServiceError(ServiceError):
    layer_instance_class_name = 'UserAuthService'


class GroupServiceException(ServiceError):
    layer_instance_class_name = 'GroupService'
