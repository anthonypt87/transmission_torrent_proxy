import os
import transmissionrpc
import unittest

import config
import transmission_torrent_proxy


class CanGetServerInformationIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.client = transmission_torrent_proxy.get_transmission_client()
        self.test_torrent_file = 'magnet:?xt=urn:btih:0e7439694e6fda56cd9c429fbff14feeab79f2b2&dn=The+Wolf+of+Wall+Street+-+Jordan+Belfort.epub&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'
        self._wipe_test_torrent()

    def tearDown(self):
        self._wipe_test_torrent()

    def _wipe_test_torrent(self):
        torrents = self.client.get_torrents()
        for torrent in torrents:
            if torrent.name in [
                'The Wolf of Wall Street - Jordan Belfort.epub',
                'The+Wolf+of+Wall+Street+-+Jordan+Belfort.epub'
            ]:
                self.client.remove_torrent([torrent.id], delete_data=True)

    def test_adds_jobs_and_writes_file(self):
        ttp = transmission_torrent_proxy.TransmissionTorrentProxy(self.client)
        ttp.add_torrent(self.test_torrent_file)

        with open(config.status_file, 'r') as status_file:
            results = status_file.read()

        self.assertNotEqual(results, '')

    def test_doesnt_download_if_file_not_done(self):
        ttp = transmission_torrent_proxy.TransmissionTorrentProxy(self.client)
        ttp.add_torrent(self.test_torrent_file)
        ttp.download_results_if_any_done()
        self.assertEqual(
            os.listdir(config.output_directory),
            []
        )
        with open(config.status_file, 'r') as status_file:
            results = status_file.read()
        self.assertNotEqual(results, '')

if __name__ == '__main__':
    unittest.main()
