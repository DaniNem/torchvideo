import os
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

import torchvideo
from torchvideo.datasets import ImageFolderVideoDataset, VideoFolderDataset


@pytest.fixture
def mock_frame_count(monkeypatch):
    def get_videofile_frame_count(path):
        return 10

    monkeypatch.setattr(
        torchvideo.datasets, "_get_videofile_frame_count", get_videofile_frame_count
    )


@pytest.fixture()
def dataset_dir(fs: FakeFilesystem):
    path = "/tmp/dataset"
    fs.create_dir(path)
    return path


class TestImageFolderVideoDatasetUnit:
    def test_all_videos_folders_are_present_in_video_dirs_by_default(self, dataset_dir):
        video_count = 10
        for i in range(0, video_count):
            os.makedirs(os.path.join(dataset_dir, "video{}".format(i)))

        dataset = ImageFolderVideoDataset(dataset_dir, "frame_{:05d}.jpg")

        assert len(dataset.video_dirs) == video_count

    def test_filtering_video_folders(self, dataset_dir):
        video_count = 10
        for i in range(0, video_count):
            os.makedirs(os.path.join(dataset_dir, "video{}".format(i)))

        def filter(video_path: Path):
            return video_path.name.endswith(("1", "2", "3"))

        dataset = ImageFolderVideoDataset(
            dataset_dir, "frame_{:05d}.jpg", filter=filter
        )

        assert len(dataset.video_dirs) == 3
        assert dataset.video_dirs[0].name == "video1"
        assert dataset.video_dirs[1].name == "video2"
        assert dataset.video_dirs[2].name == "video3"


class TestVideoFolderDatasetUnit:
    def test_all_videos_are_present_in_video_paths_by_default(
        self, dataset_dir, fs, mock_frame_count
    ):
        video_count = 10
        for i in range(0, video_count):
            path = os.path.join(dataset_dir, "video{}.mp4".format(i))
            fs.create_file(path)

        dataset = VideoFolderDataset(dataset_dir)

        assert len(dataset.video_paths) == video_count

    def test_filtering_video_files(self, dataset_dir, fs, mock_frame_count):
        video_count = 10
        for i in range(0, video_count):
            path = os.path.join(dataset_dir, "video{}.mp4".format(i))
            fs.create_file(path)

        def filter(path):
            return path.name.endswith(("1.mp4", "2.mp4", "3.mp4"))

        dataset = VideoFolderDataset(dataset_dir, filter=filter)

        assert len(dataset.video_paths) == 3
        assert dataset.video_paths[0].name == "video1.mp4"
        assert dataset.video_paths[1].name == "video2.mp4"
        assert dataset.video_paths[2].name == "video3.mp4"
