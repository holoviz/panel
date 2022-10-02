import param

class Provider(param.Parameterized):
    site = param.String(constant=True)
    title = param.String(constant=True)
    faq = param.String(constant=True)
    about = param.String(constant=True)

    temporary_collection = param.Parameter(constant=True)
    example_collection = param.Parameter(constant=True)
    saved_collection = param.Parameter(constant=True)

    auth_provider = param.Parameter(constant=True)