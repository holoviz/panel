from bokeh.command.subcommand import Subcommand

from ..compiler import (
    bundle_icons, bundle_models, bundle_resource_urls, bundle_resources,
    bundle_templates, bundle_themes,
)


class Bundle(Subcommand):
    ''' Subcommand to generate a new encryption key.

    '''

    #: name for this subcommand
    name = "bundle"

    help = "Bundle resources"

    args = (
        ('--all', dict(
            action  = 'store_true',
            help    = "Whether to bundle everything"
        )),
        ('--resource-urls', dict(
            action  = 'store_true',
            help    = "Whether to bundle the global resources"
        )),
        ('--templates', dict(
            action  = 'store_true',
            help    = "Whether to bundle the template resources"
        )),
        ('--themes', dict(
            action  = 'store_true',
            help    = "Whether to bundle the theme resources"
        )),
        ('--models', dict(
            action  = 'store_true',
            help    = "Whether to bundle the model resources"
        )),
        ('--icons', dict(
            action  = 'store_true',
            help    = "Whether to bundle icons."
        )),
        ('--verbose', dict(
            action  = 'store_true',
            help    = "Whether to print progress"
        )),
        ('--only-local', dict(
            action  = 'store_true',
            help    = "Whether to bundle only local resources"
        )),
    )

    def invoke(self, args):
        verbose = args.verbose
        if args.all:
            bundle_resources(verbose=verbose, external=not args.only_local)
            return

        if args.resource_urls:
            bundle_resource_urls(verbose=verbose, external=not args.only_local)

        if args.models:
            bundle_models(verbose=verbose, external=not args.only_local)

        if args.templates:
            bundle_templates(verbose=verbose, external=not args.only_local)

        if args.themes:
            bundle_themes(verbose=verbose, external=not args.only_local)

        if args.icons:
            bundle_icons(verbose=verbose, external=not args.only_local)
