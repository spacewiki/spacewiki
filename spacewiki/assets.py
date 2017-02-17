from flask_assets import Environment
from webassets.filter import register_filter, ExternalTool, option
import os.path

class LocalBrowserify(ExternalTool):
    name = 'local-browserify'
    max_debug_level = None
    options = {
        'transforms': option('BROWSERIFY_TRANSFORMS', type=list)
    }

    def input(self, infile, outfile, **kwargs):
        args = ['./node_modules/.bin/browserify']

        for transform in self.transforms or []:
            if isinstance(transform, (list, tuple)):
                args.extend(('--transform', '['))
                args.extend(transform)
                args.append(']')
            else:
                args.extend(('--transform', transform))

        args.append(kwargs['source_path'])

        try:
            self.subprocess(args, outfile, infile, cwd=self.ctx.directory)
        except Exception, e:
            raise Exception("Could not find browserify in %s"%(self.ctx.directory), e)

register_filter(LocalBrowserify)

ASSETS = Environment()

ASSETS.from_yaml(os.path.sep.join((os.path.dirname(__file__), 'assets.yml')))
