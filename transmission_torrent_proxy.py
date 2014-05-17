import os
import json
import config
import transmissionrpc


def get_transmission_client():
    return transmissionrpc.Client(
        config.hostname,
        port=config.port,
        user=config.user,
        password=config.password
    )


class TransmissionTorrentProxy(object):

    def __init__(self, client):
        self._client = client

    def add_torrent(self, torrent_url):
        torrent = self._client.add_torrent(torrent_url)

        with open(config.status_file, 'w') as status_file:
            status_file.write(
                json.dumps(
                    {
                        'id': torrent.id,
                        'filename': torrent.name
                    }
                )
            )

    def download_results_if_any_done(self):
        self._create_download_directory_if_not_exists()
        status = self._get_data_from_status_file()
        if not status:
            return

    def _create_download_directory_if_not_exists(self):
        if not os.path.exists(config.output_directory):
            os.mkdir(config.output_directory)

    def _get_data_from_status_file(self):
        with open(config.status_file, 'r') as status_file:
            raw_data = status_file.read()
            if not raw_data:
                return
            else:
                return json.loads(raw_data)
