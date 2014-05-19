import subprocess
import os
import json
import config
import transmissionrpc


class Status(object):
    DOWNLOADING_TORRENT = 'downloading_torrent'
    DOWNLOADING = 'downloading'
    COMPLETE = 'download_complete'


def get_transmission_client():
    return transmissionrpc.Client(
        config.hostname,
        port=config.port,
        user=config.user,
        password=config.password
    )


class TransmissionTorrentProxy(object):

    def __init__(
        self,
        client,
        os_client=None
    ):
        self._client = client
        self._os_client = os_client or OSClient()

    def add_torrent(self, torrent_url):
        torrent = self._client.add_torrent(torrent_url)
        self._os_client.merge_status({
            torrent.id: Status.DOWNLOADING_TORRENT
        })

    def download_results_if_any_done(self):
        self._os_client.create_download_directory_if_not_exists()
        status = self._os_client.get_data_from_status_file()
        if not status:
            return
        for torrent_id, torrent_status in status.iteritems():
            if torrent_status == Status.DOWNLOADING_TORRENT:
                torrent = self._client.get_torrent(torrent_id)
                if torrent.status == 'seeding':
                    for torrent_file in torrent.get_files().values():
                        remote_filename = os.path.join(
                            torrent.downloadDir,
                            torrent_file['name']
                        )
                        self._os_client.download(remote_filename)
                self._os_client.merge_status({torrent.id: Status.COMPLETE})


class OSClient(object):

    def get_data_from_status_file(self):
        with open(config.status_file, 'r') as status_file:
            raw_data = status_file.read()
            if not raw_data:
                return
            else:
                return json.loads(raw_data)

    def create_download_directory_if_not_exists(self):
        if not os.path.exists(config.output_directory):
            os.mkdir(config.output_directory)

    def merge_status(self, data):
        with open(config.status_file, 'w+') as status_file:
            raw_data = status_file.read()
            if raw_data:
                data_to_write = json.loads(raw_data)
            else:
                data_to_write = {}

            data_to_write.update(data)

            status_file.write(json.dumps(data))

    def download(self, path):
        args = [
            'rsync',
            'avz',
            '%s@%s:%s' % (
                config.username,
                config.hostname,
                path
            ),
            config.output_directory
        ]

        subprocess.call(args)
