import random 
import itertools
import PIL.Image
from pathlib import Path
from typing import Dict, List 
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    afx,
)

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

RESOLUTION = (1080, 1920)


def create_video(
    video_blocks: Dict[str, List[Path]],
    audio_blocks: Dict[str, List[Path]],
    tts_files: List[Path],
    task_name: str,
    output_folder: Path
) -> List[Path]:
    
    print(f"Starting creating video in {output_folder.name}")

    generated = []

    all_comb = list(itertools.product(*video_blocks.values()))
    
    all_music = []
    if audio_blocks:
        all_music = [p for sublist in audio_blocks.values() for p in sublist]


    tts_iterator = None
    if tts_files:
        tts_iterator = itertools.cycle(tts_files)

    for i, combo in enumerate(all_comb):

        output_file = f"{task_name}_comb_{i}.mp4"
        output_path = output_folder / output_file


        res_to_close = []

        try:
            videos = []
            for video_path in combo:
                clip = VideoFileClip(str(video_path))
                res_to_close.append(clip)

                if clip.size != RESOLUTION:
                    clip = clip.resize(newsize=RESOLUTION)
                
                videos.append(clip)
            
            final_video = concatenate_videoclips(videos, method='compose')


            voice_audio = None
            if tts_files:
                tts_path = next(tts_iterator)
                ac = AudioFileClip(str(tts_path))
                res_to_close.append(ac)

                voice_audio = ac.set_start(0)

                

            background_audio = None
            all_music=[p for sublist in audio_blocks.values() for p in sublist]

            if all_music:
                music_path = random.choice(all_music)
                bg_music = AudioFileClip(str(music_path))
                res_to_close.append(bg_music)

                bg_music = bg_music.volumex(0.2)

                duration = max(final_video.duration, voice_audio.duration if voice_audio else 0)
                bg_music= afx.audio_loop(bg_music, duration=duration)
                background_audio = bg_music

            
            audio_layers = []
            if voice_audio: audio_layers.append(voice_audio)
            if background_audio: audio_layers.append(background_audio)

            if audio_layers:
                mixed_audio = CompositeAudioClip(audio_layers)
                mixed_audio = mixed_audio.set_duration(final_video.duration)
                final_video.audio = mixed_audio
                

            final_video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset="ultrafast",
                threads=4,
                logger=None
            )


            generated.append(output_path)

        except Exception as e:
            print(f"Error in {i}: {e}")
            continue

        finally: 
            for res in res_to_close:
                try: res.close()
                except: pass

    if not generated:
        raise RuntimeError("Error! Any video doesn't created")
    return generated 