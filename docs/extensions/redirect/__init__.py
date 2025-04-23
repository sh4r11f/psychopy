from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective


class PreviousDirective(SphinxDirective):
    """
    Indicates the target page as the former location of the current page. On compile, will create a 
    .html file in that location which redirects to the document containing the directive.
    """

    has_content = True

    def run(self):
        self.assert_has_content()
        # iterate through lines in content
        for content in self.content:
            if " > " in content:
                # if given a to and from, use both
                from_raw, to_raw = content.split(" > ")
            else:
                # otherwise use current page
                to_raw = self.get_source_info()[0]
                from_raw = content
            # add redirect
            add_redirect(
                self.env, 
                from_raw=from_raw, 
                to_raw=to_raw
            )

        return []


class RedirectDirective(SphinxDirective):
    """
    Indicates the target page as the new location of the current page. On compile, will create a 
    redirect element in the file containing the directive which links to the target page.
    """
    has_content = True

    def run(self):
        self.assert_has_content()
        # iterate through lines in content
        for content in self.content:
            # get target to redirect to
            to_raw = content
            # get document to redirect from
            from_raw = self.get_source_info()[0]
            # add redirect
            add_redirect(
                self.env, 
                from_raw=from_raw, 
                to_raw=to_raw
            )

        return []


def add_redirect(env, from_raw, to_raw):
    """
    Add a redirect from one location to another.

    Parameters
    ----------
    env : sphinx.environment.BuildEnvironment
        The current Sphinx build environment
    from_raw : str
        Raw content pointing to the document to redirect from
    to_raw : str
        Raw content pointing to the document to redirect to
    """
    # make sure environment has a value for redirects
    if not hasattr(env, 'redirects'):
        env.redirects = []
    # get document to redirect from
    from_doc = env.path2doc(
        env.relfn2path(from_raw)[0]
    )
    # get url to redirect to
    if to_raw.startswith("https:"):
        # if it's an external url, point to it as is
        to_url = to_raw
    else:
        # otherwise get a relative link
        to_doc = env.path2doc(
            env.relfn2path(to_raw)[0]
        )
        to_url = f"/{to_doc}"
    # append to list of redirects
    env.redirects.append(
        (from_doc, to_url)
    )

    
def create_redirect_pages(app):
    """
    Creates the redirect pages specified in `app.env.redirects` - indended for use as an event 
    callback for the `html-collect-pages` event.
    """
    # make sure environment has a value for redirects
    if not hasattr(app.env, 'redirects'):
        app.env.redirects = []
    # get path of template for a redirect page
    templatename = str((Path(__file__).parent / "redirect.html").absolute())
    # start off with no new pages
    pages = []
    # add a new page for every redirect
    for from_doc, to_url in app.env.redirects:
        print(f"Creating redirect from {from_doc} to {to_url}.")
        # add parameters from given links
        pages.append(
            (from_doc, {'url': to_url}, templatename)
        )
    
    return pages


def setup(app):
    # add directives
    directives.register_directive('previous', PreviousDirective)
    directives.register_directive('redirect', RedirectDirective)
    # connect event callback
    app.connect('html-collect-pages', create_redirect_pages)

    return {
        'version': '0.1',
        'env_version': 1,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }