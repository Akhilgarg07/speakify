from django.contrib.auth.decorators import user_passes_test

def user_is_not_authenticated(function=None, redirect_field_name=None, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
