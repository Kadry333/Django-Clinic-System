from django.shortcuts import render


def render_page(request, template_name, current_role=None, **context):
    base_context = {"current_role": current_role}
    base_context.update(context)
    return render(request, template_name, base_context)


def login_view(request):
    return render_page(request, "accounts/login.html")


def register_view(request):
    return render_page(request, "accounts/register.html")


def dashboard_view(request):
    return render_page(
        request,
        "accounts/dashboard.html",
        current_role="Admin",
        page_title="Base Layout Preview",
    )


def users_view(request):
    return render_page(
        request,
        "accounts/manage_users.html",
        current_role="Admin",
    )
