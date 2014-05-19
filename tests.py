import mock
import os
import unittest

import config
import transmission_torrent_proxy


class TorrentProxyIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.client = transmission_torrent_proxy.get_transmission_client()
        self.test_torrent_file = 'magnet:?xt=urn:btih:0e7439694e6fda56cd9c429fbff14feeab79f2b2&dn=The+Wolf+of+Wall+Street+-+Jordan+Belfort.epub&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'
        self._wipe_test_torrent()
        self._wipe_status_file()

    def tearDown(self):
        self._wipe_test_torrent()
        self._wipe_status_file()

    def _wipe_test_torrent(self):
        torrents = self.client.get_torrents()
        for torrent in torrents:
            if torrent.name in [
                'The Wolf of Wall Street - Jordan Belfort.epub',
                'The+Wolf+of+Wall+Street+-+Jordan+Belfort.epub'
            ]:
                self.client.remove_torrent([torrent.id], delete_data=True)

    def _wipe_status_file(self):
        if os.path.exists(config.status_file):
            os.unlink(config.status_file)

    def test_adds_jobs_and_writes_file(self):
        ttp = transmission_torrent_proxy.TransmissionTorrentProxy(self.client)
        ttp.add_torrent(self.test_torrent_file)
        self._assert_status_file_has_things()

    def _assert_status_file_has_things(self):
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
        self._assert_status_file_has_things()


class TorrentProxyUnitTest(unittest.TestCase):

    def test_downloads_file_if_done(self):
        torrent_client = mock.Mock()
        os_client = mock.Mock()
        tp = transmission_torrent_proxy.TransmissionTorrentProxy(
            torrent_client,
            os_client
        )

        os_client.get_data_from_status_file.return_value = {
            '1': transmission_torrent_proxy.Status.DOWNLOADING_TORRENT
        }

        torrent = mock.Mock(
            id='1',
            downloadDir='downloadDir',
            status='seeding'
        )
        torrent.get_files.return_value = {0: {'name': 'name'}}
        torrent_client.get_torrent.return_value = torrent

        tp.download_results_if_any_done()

        os_client.download.assert_called_once_with(
            'downloadDir/name'
        )
        os_client.merge_status.assert_called_once_with(
            {'1': transmission_torrent_proxy.Status.COMPLETE}
        )


if __name__ == '__main__':
    unittest.main()
