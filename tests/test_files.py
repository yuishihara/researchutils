from researchutils import files
from mock import patch
import tempfile
import argparse
import datetime
import pytest
import os
from pathlib import Path


class TestFiles(object):
    def _mkdir(self, *pathsegments):
        filepath = Path(*pathsegments)
        if not filepath.exists():
            filepath.mkdir()
        return filepath

    def _touch(self, *pathsegments):
        filepath = Path(*pathsegments)
        filepath.touch()
        return filepath

    def test_search_all_files_under(self):
        rootdir = self._mkdir(tempfile.tempdir, 'rootdir')
        leafdir1 = self._mkdir(rootdir.resolve(), 'leafdir1')
        leafdir2 = self._mkdir(rootdir.resolve(), 'leafdir2')

        dirs = [rootdir, leafdir1, leafdir2]
        filenames = ['test1', 'test2', 'test3']
        exts = ['.txt', '.md']

        for d in dirs:
            for filename in filenames:
                for ext in exts:
                    self._touch(d.resolve(), filename + ext)

        foundfiles = files.search_all_files_under(rootdir.resolve())
        assert len(foundfiles) == len(dirs) * len(filenames) * len(exts)

        foundfiles = files.search_all_files_under(
            rootdir.resolve(), exts=['.txt'])
        assert len(foundfiles) == len(dirs) * len(filenames) * 1

        foundfiles = files.search_all_files_under(
            rootdir.resolve(), exts=['.md'])
        assert len(foundfiles) == len(dirs) * len(filenames) * 1

        foundfiles = files.search_all_files_under(
            leafdir1.resolve(), exts=['.md'])
        assert len(foundfiles) == len(filenames) * 1 * 1

    def test_file_exists(self):
        with patch('os.path.exists', return_value=True) as mock_exists:
            test_file = "test"
            assert files.file_exists(test_file) == True

    def test_file_does_not_exist(self):
        with patch('os.path.exists', return_value=False) as mock_exists:
            test_file = "test"
            assert files.file_exists(test_file) == False

    def test_create_dir_if_not_exist(self):
        with patch('os.path.exists', return_value=False) as mock_exists, patch('os.makedirs') as mock_mkdirs:
            test_file = "test"
            files.create_dir_if_not_exist(test_file)

            mock_exists.assert_called_once()
            mock_mkdirs.assert_called_once()

    def test_create_dir_when_exists(self):
        with patch('os.path.exists', return_value=True) as mock_exists, patch('os.makedirs') as mock_mkdirs:
            with patch('os.path.isdir', return_value=True):
                test_file = "test"
                files.create_dir_if_not_exist(test_file)

                mock_exists.assert_called_once()
                mock_mkdirs.assert_not_called()

    def test_create_dir_when_target_is_not_directory(self):
        with patch('os.path.exists', return_value=True) as mock_exists, patch('os.makedirs') as mock_mkdirs:
            with patch('os.path.isdir', return_value=False):
                with pytest.raises(RuntimeError):
                    test_file = "test"
                    files.create_dir_if_not_exist(test_file)

                    mock_exists.assert_called_once()
                    mock_mkdirs.assert_not_called()

    def test_prepare_output_dir(self):
        kwargs = dict(test1='test1', test2='test2')
        args = argparse.Namespace(**kwargs)
        with patch('os.path.exists', return_value=False), patch('researchutils.files.write_text_to_file'):
            base_dir = 'base/'
            output_dir = files.prepare_output_dir(base_dir, args)
            assert not len(output_dir) == 0

    def test_read_write_text_to_file(self):
        target_path = os.path.join(tempfile.tempdir, 'test.txt')
        time_format = '%Y-%m-%d-%H%M%S.%f'
        test_text = datetime.datetime.now().strftime(time_format)
        files.write_text_to_file(target_path, test_text)

        assert files.file_exists(target_path)

        read_text = files.read_text_from_file(target_path)
        assert read_text == test_text

    def test_save_and_load_pickle(self):
        target_path = os.path.join(tempfile.tempdir, 'test.txt')
        time_format = '%Y-%m-%d-%H%M%S.%f'
        test_binary = datetime.datetime.now().strftime(time_format)
        files.save_pickle(target_path, test_binary)

        assert files.file_exists(target_path)

        read_binary = files.load_pickle(target_path)
        assert read_binary == test_binary


if __name__ == '__main__':
    pytest.main()
