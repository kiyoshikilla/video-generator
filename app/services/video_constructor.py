import random 
import itertools
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

RESOLUTION = (1080, 1920)

def create_video(
    video_blocks: Dict[str, List[Path]],
    audio_blocks: Dict[str, List[Path]],
    tts_files: List[Path],
    task_name: str,
    output_folder: Path
) -> Path:
    
    print(f"Starting creating video in {output_path.name}")

    generated = []

    all_comb = list(itertools.product(*video_blocks.values()))
    
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
                tts_clips = []
                for tts_path in tts_files:
                    ac = AudioFileClip(str(tts_path))
                    tts_clips.append(ac)
                    res_to_close.append(ac)
                if tts_clips:
                    voice_audio = concatenate_audioclips(tts_clips)
                

            background_audio = None
            all_music=[p for sublist in audio_blocks.values() for p in sublist]

            if all_music:
                music_path = random.choice(all_music)
                bg_music = AudioFileClip(str(music_path))
                res_to_close.append(bg_music)

                bg_music = bg_music.vol(0.2)

                duration = max(final_video.duration, voice_audio.duration if voice_audio else 0)
                bg_music= afx.audio_loop(bg_music, duration=duration)
                background_audio = bg_music

            
            audio_layers = []
            if voice_audio: audio_layers.apend(voice_audio)
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


    return generated 