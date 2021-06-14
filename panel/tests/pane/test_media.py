import pathlib

from panel.pane import Audio, Video

ASSETS = pathlib.Path(__file__).parent / 'assets'


def test_video_url(document, comm):
    url = 'https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4'
    video = Video(url)
    model = video.get_root(document, comm=comm)

    # To check if url is send to the bokeh model
    assert model.value == url


def test_local_video(document, comm):
    video = Video(str(ASSETS / 'mp4.mp4'))
    model = video.get_root(document, comm=comm)

    # To check if url is send to the bokeh model
    assert model.value == 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAAAAhtZGF0AAAA1m1vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAAAAAAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAABidWR0YQAAAFptZXRhAAAAAAAAACFoZGxyAAAAAAAAAABtZGlyYXBwbAAAAAAAAAAAAAAAAC1pbHN0AAAAJal0b28AAAAdZGF0YQAAAAEAAAAATGF2ZjU3LjQxLjEwMA=='


def test_local_audio(document, comm):
    audio = Audio(str(ASSETS / 'mp3.mp3'))
    model = audio.get_root(document, comm=comm)

    # To check if url is send to the bokeh model
    assert model.value == 'data:audio/mp3;base64,/+MYxAAAAANIAAAAAExBTUUzLjk4LjIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
