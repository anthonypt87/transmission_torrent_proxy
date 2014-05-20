import subprocess
import os
import json
import config
import transmissionrpc


class Status(object):
    TORRENTING = 'torrenting'
    TRANSFERRING = 'transferring'
    COMPLETE = 'complete'


def get_transmission_client():
    return transmissionrpc.Client(
        config.hostname,
        port=config.port,
        user=config.user,
        password=config.password
    )


class TransmissionTorrentProxy(object):

    def __init__(self, client, os_client=None):
        self._client = client
        self._os_client = os_client or OSClient()

    def add_torrent(self, torrent_url):
        torrent = self._client.add_torrent(torrent_url)
        self._os_client.update_status(torrent.id, Status.TORRENTING)

    def download_results_if_any_done(self):
        self._os_client.create_download_directory_if_not_exists()

        status = self._os_client.get_data_from_status_file()
        if not status:
            return

        for torrent_id, torrent_status in status.iteritems():
            if torrent_status != Status.TORRENTING:
                continue

            torrent = self._client.get_torrent(torrent_id)
            if torrent.status == 'seeding':
                self._download_all_files(torrent)
            self._os_client.update_status(torrent.id, Status.COMPLETE)

    def _download_all_files(self, torrent):
        for torrent_file in torrent.get_files().values():
            remote_filename = os.path.join(
                torrent.downloadDir,
                torrent_file['name']
            )
            self._os_client.download(remote_filename)


class OSClient(object):

    def get_data_from_status_file(self):
        with open(config.status_file, 'r') as status_file:
            raw_data = status_file.read()
            if not raw_data:
                return
            return json.loads(raw_data)

    def create_download_directory_if_not_exists(self):
        if not os.path.exists(config.output_directory):
            os.mkdir(config.output_directory)

    def update_status(self, _id, status):
        with open(config.status_file, 'w+') as status_file:
            raw_data = status_file.read()
            if raw_data:
                data_to_write = json.loads(raw_data)
            else:
                data_to_write = {}

            data_to_write[_id] = status
            status_file.write(json.dumps(data_to_write))

    def download(self, path):
        source = '%s@%s:%s' % (config.username, config.hostname, path)
        args = [
            'rsync',
            '--avz',
            source,
            config.output_directory
        ]

        subprocess.call(args)
