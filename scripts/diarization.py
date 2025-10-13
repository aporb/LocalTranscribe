#!/usr/bin/env python3
"""
Speaker Diarization Script for macOS M4 Pro
Using pyannote/speaker-diarization-community-1

This script performs speaker diarization on audio files with:
- Automatic audio preprocessing (mono, 16kHz)
- GPU acceleration on Apple Silicon (MPS)
- Progress monitoring
- Exclusive speaker diarization
- Speaker count control
- Offline processing capability
"""

import torch
import torchaudio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pydub import AudioSegment
import os
import warnings
from dotenv import load_dotenv
import time

# Suppress torchcodec warnings (common issue with FFmpeg versions)
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote.audio")

def setup_device():
    """Configure optimal device for macOS M4 Pro"""
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        print("🚀 Using Apple Silicon GPU acceleration (MPS) on M4 Pro")
        # Optimize for M4 Pro
        torch.set_num_threads(10)  # M4 Pro has 10 CPU cores
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        print("🚀 Using CUDA GPU acceleration")
    else:
        device = torch.device('cpu')
        print("💻 Using CPU processing")
    
    return device

def preprocess_audio(input_file):
    """Preprocess audio file to optimal format for pyannote"""
    print(f"📁 Processing audio file: {input_file}")

    # Get base name and prepare output path
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Convert to WAV if needed and ensure proper format
    if input_file.endswith('.ogg'):
        print("🔄 Converting OGG to WAV...")
        audio = AudioSegment.from_ogg(input_file)
        wav_file = f"../input/{base_name}.wav"

        # Convert to mono and 16kHz as required by pyannote
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_file, format='wav')
        print(f"✅ Conversion complete: {wav_file}")
        return wav_file
    else:
        # For other formats, ensure they're in the right format
        audio = AudioSegment.from_file(input_file)
        if audio.frame_rate != 16000 or audio.channels != 1:
            print("🔄 Resampling to 16kHz mono...")
            audio = audio.set_frame_rate(16000).set_channels(1)
            wav_file = f"../input/{base_name}_processed.wav"
            audio.export(wav_file, format='wav')
            print(f"✅ Preprocessing complete: {wav_file}")
            return wav_file
        return input_file

def load_pipeline(token):
    """Load the pyannote speaker diarization pipeline"""
    print("📥 Loading pyannote/speaker-diarization-community-1...")
    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-community-1",
            token=token
        )
        print("✅ Pipeline loaded successfully!")
        return pipeline
    except Exception as e:
        print(f"❌ Failed to load pipeline: {e}")
        raise

def run_diarization(pipeline, audio_file, device, num_speakers=None, min_speakers=None, max_speakers=None):
    """Run speaker diarization with progress monitoring"""
    print("🎯 Starting speaker diarization...")
    
    # Move pipeline to GPU if available
    if device.type == 'mps' or device.type == 'cuda':
        print(f"⚡ Moving pipeline to {device} for faster processing...")
        pipeline.to(device)
    
    # Prepare arguments
    diarization_args = {}
    if num_speakers:
        diarization_args['num_speakers'] = num_speakers
        print(f"🎤 Specified number of speakers: {num_speakers}")
    if min_speakers:
        diarization_args['min_speakers'] = min_speakers
        print(f"🎤 Minimum speakers: {min_speakers}")
    if max_speakers:
        diarization_args['max_speakers'] = max_speakers
        print(f"🎤 Maximum speakers: {max_speakers}")
    
    # Load audio using torchaudio to avoid torchcodec issues
    print("📁 Loading audio with torchaudio...")
    try:
        waveform, sample_rate = torchaudio.load(audio_file)
        print(f"✅ Audio loaded: {waveform.shape[1]/sample_rate:.2f}s duration")
        
        # Run diarization with preloaded audio
        start_time = time.time()
        with ProgressHook() as hook:
            output = pipeline({"waveform": waveform, "sample_rate": sample_rate}, hook=hook, **diarization_args)
        
        processing_time = time.time() - start_time
        print(f"⏱️  Processing completed in {processing_time:.2f} seconds")
        
        return output
        
    except Exception as e:
        print(f"⚠️  Torchaudio loading failed: {e}")
        print("🔄 Falling back to file path method...")
        
        # Fallback to file path method
        start_time = time.time()
        with ProgressHook() as hook:
            output = pipeline(audio_file, hook=hook, **diarization_args)
        
        processing_time = time.time() - start_time
        print(f"⏱️  Processing completed in {processing_time:.2f} seconds")
        
        return output

def write_markdown_results(output, audio_file, show_exclusive=True):
    """Write diarization results to a Markdown file"""
    import datetime
    
    # Create markdown filename based on audio file
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    md_filename = f"../output/{base_name}_diarization_results.md"
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# Speaker Diarization Results\n\n")
        f.write(f"**Audio File:** {audio_file}\n\n")
        f.write(f"**Processing Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Regular speaker diarization
        f.write("## Regular Speaker Diarization\n\n")
        f.write("| Speaker | Start Time (s) | End Time (s) | Duration (s) |\n")
        f.write("|---------|----------------|--------------|--------------|\n")
        
        for turn, speaker in output.speaker_diarization:
            duration = turn.end - turn.start
            f.write(f"| {speaker} | {turn.start:.3f} | {turn.end:.3f} | {duration:.3f} |\n")
        
        f.write("\n")
        
        # Exclusive speaker diarization (if available)
        if show_exclusive and hasattr(output, 'exclusive_speaker_diarization'):
            f.write("## Exclusive Speaker Diarization\n\n")
            f.write("| Speaker | Start Time (s) | End Time (s) | Duration (s) |\n")
            f.write("|---------|----------------|--------------|--------------|\n")
            
            for turn, speaker in output.exclusive_speaker_diarization:
                duration = turn.end - turn.start
                f.write(f"| {speaker} | {turn.start:.3f} | {turn.end:.3f} | {duration:.3f} |\n")
            
            f.write("\n")
        
        # Summary statistics
        speakers = set()
        total_duration = 0
        for turn, speaker in output.speaker_diarization:
            speakers.add(speaker)
            total_duration += turn.end - turn.start
        
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total speakers detected:** {len(speakers)}\n")
        f.write(f"- **Total speech duration:** {total_duration:.3f}s\n")
        f.write(f"- **Speakers:** {', '.join(sorted(speakers))}\n")
        f.write(f"- **Total speaker turns:** {len(list(output.speaker_diarization))}\n")
        
        # Additional statistics
        speaker_durations = {}
        for turn, speaker in output.speaker_diarization:
            if speaker not in speaker_durations:
                speaker_durations[speaker] = 0
            speaker_durations[speaker] += turn.end - turn.start
        
        f.write("\n### Speaker Time Distribution\n\n")
        for speaker in sorted(speaker_durations.keys()):
            duration = speaker_durations[speaker]
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            f.write(f"- **{speaker}:** {duration:.3f}s ({percentage:.1f}% of total speech)\n")
    
    print(f"📄 Markdown results saved to: {md_filename}")
    return md_filename

def print_results(output, show_exclusive=True):
    """Print diarization results in a clear format"""
    print("\n" + "="*80)
    print("🎯 SPEAKER DIARIZATION RESULTS")
    print("="*80)
    
    # Regular speaker diarization
    print("\n📊 Regular Speaker Diarization:")
    print("-" * 50)
    for turn, speaker in output.speaker_diarization:
        duration = turn.end - turn.start
        print(f"Speaker '{speaker}' speaks from {turn.start:.3f}s to {turn.end:.3f}s (duration: {duration:.3f}s)")
    
    # Exclusive speaker diarization (if available)
    if show_exclusive and hasattr(output, 'exclusive_speaker_diarization'):
        print("\n🎯 Exclusive Speaker Diarization:")
        print("-" * 50)
        for turn, speaker in output.exclusive_speaker_diarization:
            duration = turn.end - turn.start
            print(f"Speaker '{speaker}' speaks from {turn.start:.3f}s to {turn.end:.3f}s (duration: {duration:.3f}s)")
    
    # Summary statistics
    speakers = set()
    total_duration = 0
    for turn, speaker in output.speaker_diarization:
        speakers.add(speaker)
        total_duration += turn.end - turn.start
    
    print(f"\n📈 Summary:")
    print(f"   • Total speakers detected: {len(speakers)}")
    print(f"   • Total speech duration: {total_duration:.3f}s")
    print(f"   • Speakers: {', '.join(sorted(speakers))}")

def main():
    """Main execution function"""
    print("🎙️  Speaker Diarization for macOS M4 Pro")
    print("="*50)
    
    # Setup device
    device = setup_device()
    
    # Load environment variables
    load_dotenv('.env')
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    
    if not hf_token or hf_token == "your_token_here":
        print("❌ Hugging Face token not found!")
        print("💡 Please add HUGGINGFACE_TOKEN=\"your_token\" to your .env file")
        print("   Get your token from: https://huggingface.co/settings/tokens")
        return
    
    print(f"🔑 Using Hugging Face token: {hf_token[:10]}...")
    
    # Audio file processing
    audio_file = "../input/audio.ogg"  # Change this to your audio file in input/ folder
    if not os.path.exists(audio_file):
        print(f"❌ Audio file '{audio_file}' not found!")
        print("💡 Please place your audio file in the input/ directory")
        return
    
    # Preprocess audio
    processed_file = preprocess_audio(audio_file)
    
    try:
        # Load pipeline
        pipeline = load_pipeline(hf_token)
        
        # Run diarization (specify 2 speakers for your use case)
        output = run_diarization(
            pipeline, 
            processed_file, 
            device,
            num_speakers=2,  # You can change this or remove it for automatic detection
            min_speakers=1,
            max_speakers=3
        )
        
        # Print results and save to markdown
        print_results(output, show_exclusive=True)
        write_markdown_results(output, processed_file, show_exclusive=True)
        
        print(f"\n✅ Speaker diarization completed successfully!")
        print(f"📄 Markdown results saved to: {os.path.splitext(os.path.basename(processed_file))[0]}_diarization_results.md")
        print(f"🔒 All processing done locally on your M4 Pro - no internet required!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temporary files
        if processed_file != audio_file and os.path.exists(processed_file):
            try:
                os.remove(processed_file)
                print(f"🧹 Cleaned up temporary file: {processed_file}")
            except Exception as e:
                print(f"⚠️  Could not remove temporary file: {e}")

if __name__ == "__main__":
    main()
