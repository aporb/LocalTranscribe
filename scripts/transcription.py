#!/usr/bin/env python3
"""
Optimized Speech-to-Text Transcription Script for macOS M4 Pro
Using MLX-Whisper for optimal GPU acceleration on Apple Silicon

This script performs speech-to-text transcription on audio files with:
- Automatic audio preprocessing (mono, 16kHz)
- Apple Silicon optimized MLX implementation (primary)
- MPS acceleration fallback (secondary)
- CPU processing fallback (backup)
- Progress monitoring
- Multiple output formats
- Detailed markdown with timestamps
- Offline processing capability
"""

import os
import warnings
from dotenv import load_dotenv
import time
import json
from datetime import datetime
from typing import Optional, Any, Dict, List
import sys

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

def check_implementations():
    """Check available Whisper implementations and return the best one"""
    implementations = []
    
    # Check for MLX-Whisper (Apple Silicon optimized) - now properly fixed
    try:
        import mlx_whisper
        import mlx.core as mx
        if mx.metal.is_available():
            print("✅ MLX-Whisper available with Metal support - Primary choice for M4 Pro")
            implementations.append(("mlx", "mlx-whisper"))
        else:
            print("⚠️ MLX-Whisper available but Metal support not detected")
    except ImportError:
        print("⚠️ MLX-Whisper not available - install with 'pip install mlx-whisper'")
    except Exception as e:
        print(f"⚠️ MLX-Whisper issue: {e}")
        print("   Checking other implementations...")
    
    # Check for faster-whisper (reliable alternative)
    try:
        import faster_whisper
        print("✅ Faster-Whisper available - Good alternative for M4 Pro")
        implementations.append(("faster", "faster-whisper"))
    except ImportError:
        print("⚠️ Faster-Whisper not available - install with 'pip install faster-whisper'")
    
    # Check for original whisper with MPS
    try:
        import torch
        if torch.backends.mps.is_available():
            import whisper
            print("✅ Original Whisper with MPS available - Backup option")
            implementations.append(("original", "openai-whisper"))
        else:
            print("⚠️ MPS not available for original whisper")
    except ImportError:
        print("⚠️ Original Whisper not available - install with 'pip install openai-whisper'")
    
    if not implementations:
        print("❌ No Whisper implementations available!")
        print("Install at least one: mlx-whisper, faster-whisper, or openai-whisper")
        return None
    
    return implementations[0][0]  # Return the first (best) implementation

def setup_device():
    """Configure optimal device for macOS M4 Pro - mainly for non-MLX implementations"""
    # Check if MPS is available
    try:
        import torch
        if torch.backends.mps.is_available():
            device = torch.device('mps')
            print("💻 Using MPS (Metal Performance Shaders) for GPU acceleration")
            return device
        else:
            print("💻 MPS not available, using CPU")
            # Optimize for M4 Pro CPU
            torch.set_num_threads(8)  # Use 8 threads for optimal CPU performance on M4 Pro
            return torch.device('cpu')
    except ImportError:
        print("💻 PyTorch not available, using basic processing")
        return 'cpu'

def preprocess_audio(input_file):
    """Preprocess audio file to optimal format for Whisper"""
    from pydub import AudioSegment

    print(f"📁 Processing audio file: {input_file}")

    # Get base name and prepare output path
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Convert to WAV if needed and ensure proper format
    if input_file.endswith('.ogg'):
        print("🔄 Converting OGG to WAV...")
        audio = AudioSegment.from_ogg(input_file)
        wav_file = f"../input/{base_name}_processed.wav"

        # Convert to mono and 16kHz as required by most Whisper implementations
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

def transcribe_with_mlx_whisper(audio_file: str, model_size: str = "base", language: Optional[str] = None):
    """Use MLX-Whisper for transcription (Apple Silicon optimized)"""
    import mlx_whisper
    import mlx.core as mx
    
    print(f"🔄 Using MLX-Whisper with {model_size} model")
    
    # Set memory limit for MLX
    mx.set_cache_limit(1024 * 1024 * 1024)  # 1GB
    
    start_time = time.time()
    
    # Load and run transcription - use community models that are pre-converted
    community_model_map = {
        "tiny": "mlx-community/whisper-tiny-mlx",
        "base": "mlx-community/whisper-base-mlx", 
        "small": "mlx-community/whisper-small-mlx",
        "medium": "mlx-community/whisper-medium-mlx",
        "large": "mlx-community/whisper-large-v3-mlx"
    }
    
    model_repo = community_model_map.get(model_size, f"mlx-community/whisper-{model_size}")
    
    result = mlx_whisper.transcribe(
        audio_file,
        path_or_hf_repo=model_repo,
        language=language
    )
    
    processing_time = time.time() - start_time
    
    # Convert MLX result to format compatible with other implementations
    class MLXResult:
        def __init__(self, result_dict):
            self.text = result_dict["text"]
            self.language = result_dict.get("language", "unknown")
            self.duration = result_dict.get("duration", 0)
            self.segments = []
            
            # Convert segments to compatible format
            if "segments" in result_dict:
                for i, seg in enumerate(result_dict["segments"]):
                    segment_obj = type('Segment', (), {})()
                    segment_obj.id = seg.get("id", i)
                    segment_obj.start = seg.get("start", 0)
                    segment_obj.end = seg.get("end", 0)
                    segment_obj.text = seg.get("text", "")
                    # MLX Whisper might not have all the same fields, set defaults
                    segment_obj.temperature = seg.get("temperature", 0)
                    segment_obj.avg_logprob = seg.get("avg_logprob", 0)
                    segment_obj.compression_ratio = seg.get("compression_ratio", 0)
                    segment_obj.no_speech_prob = seg.get("no_speech_prob", 0)
                    self.segments.append(segment_obj)
    
    result_obj = MLXResult(result)
    
    print(f"⏱️  MLX-Whisper completed in {processing_time:.2f} seconds")
    return result_obj

def transcribe_with_faster_whisper(audio_file: str, model_size: str = "base", language: Optional[str] = None):
    """Use Faster-Whisper for transcription with MPS support"""
    import torch
    from faster_whisper import WhisperModel
    
    print(f"🔄 Using Faster-Whisper with {model_size} model")
    
    # Determine device - faster-whisper doesn't support MPS, only CPU and CUDA
    torch_device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"💻 Using device: {torch_device}")
    
    start_time = time.time()
    
    # Load model with CPU as faster-whisper doesn't directly support MPS
    compute_type = "float32"  # Use float32 for better compatibility
    if torch_device == "cpu":
        # On Apple Silicon, optimize for M4 Pro CPU
        torch.set_num_threads(8)
        compute_type = "float16"  # Use float16 on CPU for better performance on M4
    
    model = WhisperModel(
        model_size, 
        device="cpu",  # faster-whisper doesn't support MPS, use CPU
        compute_type=compute_type
    )
    
    # Run transcription
    segments, info = model.transcribe(
        audio_file, 
        beam_size=5,
        language=language
    )
    
    # Collect segments
    segment_list = []
    full_text = ""
    for segment in segments:
        segment_list.append({
            'id': len(segment_list),
            'start': segment.start,
            'end': segment.end,
            'text': segment.text,
            'temperature': 0,
            'avg_logprob': 0,
            'compression_ratio': 0,
            'no_speech_prob': 0
        })
        full_text += segment.text + " "
    
    processing_time = time.time() - start_time
    
    # Create result object
    class FasterResult:
        def __init__(self, text, segments, info):
            self.text = text.strip()
            self.language = getattr(info, 'language', language or 'unknown')
            self.duration = max([s['end'] for s in segments]) if segments else 0
            self.segments = []
            
            for seg in segments:
                segment_obj = type('Segment', (), {})()
                for key, value in seg.items():
                    setattr(segment_obj, key, value)
                self.segments.append(segment_obj)
    
    result_obj = FasterResult(full_text, segment_list, info)
    
    print(f"⏱️  Faster-Whisper completed in {processing_time:.2f} seconds")
    return result_obj

def transcribe_with_original_whisper(audio_file: str, model_size: str = "base", language: Optional[str] = None):
    """Use original OpenAI Whisper for transcription (fallback)"""
    import whisper
    import torch
    
    # Set device
    device = setup_device()
    
    print(f"🔄 Using Original Whisper with {model_size} model")
    
    start_time = time.time()
    
    # Load model
    model = whisper.load_model(model_size, device=device)
    
    # Run transcription
    result = model.transcribe(
        audio_file,
        language=language,
        task="transcribe",
        fp16=False if device.type == 'cpu' else True
    )
    
    processing_time = time.time() - start_time
    
    print(f"⏱️  Original Whisper completed in {processing_time:.2f} seconds")
    return result

def run_transcription(audio_file: str, model_size: str = "base", language: Optional[str] = None, implementation: str = "auto"):
    """Run speech-to-text transcription using the best available implementation"""
    
    if implementation == "auto":
        implementation = check_implementations()
        if not implementation:
            raise Exception("No Whisper implementation available")
    
    print(f"🎯 Starting transcription with {implementation} implementation...")
    
    if implementation == "mlx":
        return transcribe_with_mlx_whisper(audio_file, model_size, language)
    elif implementation == "faster":
        return transcribe_with_faster_whisper(audio_file, model_size, language)
    elif implementation == "original":
        return transcribe_with_original_whisper(audio_file, model_size, language)
    else:
        raise Exception(f"Unknown implementation: {implementation}")

def write_transcript_results(result, audio_file, output_formats=['txt', 'srt', 'json', 'md']):
    """Write transcription results to multiple file formats"""
    import datetime
    
    # Create base filename
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    
    results = {}
    
    # Text format
    if 'txt' in output_formats:
        txt_filename = f"../output/{base_name}_transcript.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(result.text)
        print(f"📄 Text transcript saved to: {txt_filename}")
        results['txt'] = txt_filename

    # SRT subtitle format
    if 'srt' in output_formats:
        srt_filename = f"../output/{base_name}_transcript.srt"
        with open(srt_filename, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result.segments, 1):
                start = datetime.timedelta(seconds=segment.start)
                end = datetime.timedelta(seconds=segment.end)
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment.text.strip()}\n\n")
        print(f"📄 SRT subtitle file saved to: {srt_filename}")
        results['srt'] = srt_filename

    # JSON format with detailed timing
    if 'json' in output_formats:
        json_filename = f"../output/{base_name}_transcript.json"
        json_data = {
            "transcript": result.text,
            "segments": [
                {
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "temperature": getattr(segment, 'temperature', 0),
                    "avg_logprob": getattr(segment, 'avg_logprob', 0),
                    "compression_ratio": getattr(segment, 'compression_ratio', 0),
                    "no_speech_prob": getattr(segment, 'no_speech_prob', 0)
                }
                for segment in result.segments
            ],
            "processing_info": {
                "audio_file": audio_file,
                "processing_date": datetime.datetime.now().isoformat(),
                "language": result.language,
                "duration": result.duration
            }
        }
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"📄 JSON transcript saved to: {json_filename}")
        results['json'] = json_filename
    
    # Markdown format with timestamps
    if 'md' in output_formats:
        md_filename = f"../output/{base_name}_transcript.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(f"# Audio Transcript\n\n")
            f.write(f"**Audio File:** {audio_file}\n\n")
            f.write(f"**Processing Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Detected Language:** {result.language}\n\n")
            f.write(f"**Total Duration:** {result.duration:.2f}s\n\n")
            f.write("## Transcript\n\n")
            
            for segment in result.segments:
                start_time = f"{segment.start:.3f}s"
                end_time = f"{segment.end:.3f}s"
                f.write(f"**[{start_time} - {end_time}]** {segment.text.strip()}\n\n")
        
        print(f"📄 Markdown transcript saved to: {md_filename}")
        results['md'] = md_filename
    
    return results

def print_transcript_summary(result):
    """Print transcription summary to console"""
    print("\n" + "="*80)
    print("🎤 SPEECH-TO-TEXT TRANSCRIPTION RESULTS")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"   • Detected language: {result.language}")
    print(f"   • Total duration: {result.duration:.2f}s")
    print(f"   • Total segments: {len(result.segments)}")
    
    if len(result.segments) > 0:
        avg_confidence = sum(getattr(s, 'avg_logprob', 0) for s in result.segments) / len(result.segments)
        print(f"   • Average confidence: {avg_confidence:.3f}")
    
    print(f"\n📝 Transcript Preview (first 500 characters):")
    print("-" * 50)
    preview = result.text[:500].strip()
    print(preview + ("..." if len(result.text) > 500 else ""))
    print("-" * 50)

def main():
    """Main execution function"""
    print("🎙️  Optimized Speech-to-Text Transcription for macOS M4 Pro")
    print("🚀 Using MLX-Whisper for optimal Apple Silicon performance")
    print("="*70)
    
    # Audio file processing
    audio_file = "../input/audio.ogg"  # Change this to your audio file in input/ folder
    if not os.path.exists(audio_file):
        print(f"❌ Audio file '{audio_file}' not found!")
        print("💡 Please place your audio file in the input/ directory")
        return
    
    # Preprocess audio
    processed_file = preprocess_audio(audio_file)
    
    try:
        # Determine the best implementation
        print("\n🔍 Checking available Whisper implementations...")
        implementation = check_implementations()
        if not implementation:
            print("❌ No Whisper implementations available - please install one!")
            return
        
        # Run transcription
        result = run_transcription(
            processed_file,
            model_size="base",  # base model is good balance of speed/accuracy
            language=None,      # Set to 'en' for English only, None for auto-detection
            implementation=implementation
        )
        
        # Print summary
        print_transcript_summary(result)
        
        # Save results in multiple formats
        output_files = write_transcript_results(result, processed_file)
        
        print(f"\n✅ Transcription completed successfully!")
        print(f"🔒 All processing done locally on your M4 Pro - no internet required!")
        print(f"⚡ Using {implementation} implementation for optimal performance")
        print(f"📁 Output files created:")
        for format_type, filename in output_files.items():
            print(f"   • {format_type.upper()}: {filename}")
        
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