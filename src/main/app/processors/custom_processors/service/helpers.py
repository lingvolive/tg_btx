

class SPUserManagementHelper():

    def __init__(self) -> None:
        pass

    @staticmethod
    def user_profile_menu_text(user, app_resources):
        
        profile_text  = user.profile_text(app_resources)
        message_text = f'*{app_resources.strProfile}*\n'\
                       f'{profile_text}'
        
        return message_text
    
    @staticmethod
    def user_management_menu(app_resources):
        return app_resources.mUserManageMenu
    
    @staticmethod
    def setting_name_chosen_user():
        return 'chosen_user_id'




