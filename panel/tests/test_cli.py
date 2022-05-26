from panel.command import transform_cmds


def test_transformation():
    args = ['panel', 'serve', '.',
            '--anaconda-project-host', 'host.examplehost.com',
            '--anaconda-project-port', '8086', '--anaconda-project-iframe-hosts', 'examplehost.com',
            '--anaconda-project-use-xheaders', '--anaconda-project-no-browser', '--anaconda-project-address=0.0.0.0']
    expected = ['panel', 'serve', '.', '--allow-websocket-origin', 'host.examplehost.com', '--port', '8086']
    remapped_args = transform_cmds(args)
    assert remapped_args == expected
