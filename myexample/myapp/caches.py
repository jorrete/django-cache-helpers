def get_cache_key_by_view(request, *args, **kwargs):
    return kwargs['view_path']


def get_cache_key_by_path(request, *args, **kwargs):
    return request.path
