from rest_framework.views import APIView


class SerializerGetter:
    def __init__(self, default, **kwargs):
        self.default = default
        self.serializer_per_action = kwargs

    def get_serializer_class(self, view: [APIView]):
        return self.serializer_per_action.get(
            getattr(view, 'action', None),
            self.default
        )

    def __call__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        view: APIView = context.get('view')
        serializer_class = self.get_serializer_class(view)
        return serializer_class(*args, **kwargs)


class SerializerFactory:
    def __init__(self, default, **kwargs):
        self.serializer_getter = SerializerGetter(
            default=default, **kwargs,
        )

    def __call__(self, *args, **kwargs):
        return self.serializer_getter(*args, **kwargs)