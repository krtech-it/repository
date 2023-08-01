

class BaseAdmin:
    '''
    Класс для методов администратора
    '''

    def __init__(self, manager_auth, manager_role):
        self.manager_auth = manager_auth
        self.manager_role = manager_role