def check_user_permissions(request_object, request_action, user):
    permissions = user.role.permissions

    for permission in permissions:
        print("Comparison:", request_object, permission.object)
        if request_object == permission.object:
            int_perms = permission.permissions
            return int_perms[request_action] == 1

    return True
