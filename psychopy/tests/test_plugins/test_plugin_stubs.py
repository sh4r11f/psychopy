from psychopy.plugins import PluginStub


def test_plugin_stub_urls():
    """
    Test that links (docsHome and docsRef) are combined correctly in the docstring of PluginStub
    """
    cases = [
        # docsHome with no docsRef
        {
            'plugin': "psychopy-test",
            'docsHome': "https://psychopy.com",
            'docsRef': "",
            'ans': {
                'docsHome': "https://psychopy.com",
                'docsLink': "https://psychopy.com/",
            } 
        },
        # docsHome included in docsRef
        {
            'plugin': "psychopy-test",
            'docsHome': "https://psychopy.com",
            'docsRef': "https://psychopy.com/test",
            'ans': {
                'docsHome': "https://psychopy.com",
                'docsLink': "https://psychopy.com/test",
            } 
        },
        # docsRef without /
        {
            'plugin': "psychopy-test",
            'docsHome': "https://psychopy.com",
            'docsRef': "test",
            'ans': {
                'docsHome': "https://psychopy.com",
                'docsLink': "https://psychopy.com/test",
            } 
        },
        # docsHome with /
        {
            'plugin': "psychopy-test",
            'docsHome': "https://psychopy.com/",
            'docsRef': "/test",
            'ans': {
                'docsHome': "https://psychopy.com",
                'docsLink': "https://psychopy.com/test",
            } 
        },
    ]

    for case in cases:
        # subclass PluginStub with the given values
        class TestPluginStub(
            PluginStub,
            plugin=case['plugin'],
            docsHome=case['docsHome'],
            docsRef=case['docsRef'],
        ):
            pass
        # check for the necessary strings in its docstr
        assert case['plugin'] in TestPluginStub.__doc__
        assert "<%(docsHome)s>" % case['ans'] in TestPluginStub.__doc__
        assert "<%(docsLink)s>" % case['ans'] in TestPluginStub.__doc__
            