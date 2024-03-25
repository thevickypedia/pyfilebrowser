import logging
import os
import pathlib
import threading

from pydantic import DirectoryPath


class Thread(threading.Thread):
    """Overrides the default thread, to raise an exception when thread run fails.

    >>> Thread

    """

    def run(self) -> None:
        """Runs the thread."""
        self._exc = None
        try:
            super().run()
        except Exception as e:
            self._exc = e

    def join(self, timeout=None) -> None:
        """Blocks the calling thread until the thread whose join method is called terminates.

        Args:
            timeout: Timeout for the thread to close.
        """
        super().join(timeout=timeout)
        if self._exc:
            raise self._exc


def auto_convert(root: DirectoryPath, logger: logging.Logger) -> None:
    """Get video files or folders that contain video files to be streamed."""
    n_raw = 0
    threads = {}
    for __path, __directory, __file in os.walk(root):
        if __path.endswith('__'):
            continue
        for file_ in __file:
            n_raw += 1
            if file_.startswith('_') or file_.startswith('.'):
                continue
            file = pathlib.PosixPath(str(os.path.join(__path, file_)))
            if file.suffix == ".srt":
                if file.with_suffix(".vtt").exists():
                    logger.debug(f'Both srt and vtt exists for {file.name}')
                else:
                    thread = Thread(target=srt_to_vtt, args=(file, logger,))
                    thread.start()
                    threads[file] = thread
    for file, thread in threads.items():
        try:
            thread.join()
        except Exception as error:
            logger.error(f"{error!r}:\t{file.name}")


def srt_to_vtt(filename: pathlib.PosixPath, logger: logging.Logger) -> None:
    """Convert a .srt file to .vtt for subtitles to be compatible with video-js.

    Args:
        filename: Name of the srt file.
        logger: Logger object to log conversion details.
    """
    logger.debug(f"Converting srt to vtt - {filename.name}")
    output_file = filename.with_suffix('.vtt')
    with open(filename, 'r', encoding='utf-8') as rf:
        srt_content = rf.read()
    srt_content = srt_content.replace(',', '.')
    srt_content = srt_content.replace(' --> ', '-->')
    vtt_content = 'WEBVTT\n\n'
    subtitle_blocks = srt_content.strip().split('\n\n')
    for block in subtitle_blocks:
        lines = block.split('\n')
        timecode = lines[1]
        text = '\n'.join(lines[2:])
        vtt_content += f"{timecode}\n{text}\n\n"
    with open(output_file, 'w', encoding='utf-8') as wf:
        wf.write(vtt_content)
    logger.info(f"Converted srt to vtt - {filename.name}")


def vtt_to_srt(filename: pathlib.PosixPath, logger: logging.Logger) -> None:
    """Convert a .vtt file to .srt for subtitles to be compatible with video-js.

    Args:
        filename: Name of the srt file.
        logger: Logger object to log conversion details.
    """
    logger.debug(f"Converting vtt to srt - {filename.name}")
    output_file = filename.with_suffix('.srt')
    with open(filename, 'r', encoding='utf-8') as f:
        vtt_content = f.read()
    vtt_content = vtt_content.replace('WEBVTT\n\n', '').replace('WEBVTT FILE\n\n', '')
    subtitle_blocks = vtt_content.strip().split('\n\n')
    subtitle_counter = 1
    srt_content = ''
    for block in subtitle_blocks:
        lines = block.split('\n')
        for idx, line in enumerate(lines):
            if '-->' in line:
                break
        else:
            raise RuntimeError
        text = '\n'.join(lines[idx + 1:])
        srt_timecode = line if ' --> ' in line else line.replace('-->', ' --> ')
        srt_content += f"{subtitle_counter}\n{srt_timecode}\n{text}\n\n"
        subtitle_counter += 1
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    logger.info(f"Converted vtt to srt - {filename.name}")
