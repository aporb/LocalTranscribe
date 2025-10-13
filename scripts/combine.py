#!/usr/bin/env python3
"""
Combine Speaker Diarization and Transcription Results
This script merges the speaker diarization results with the transcription
to create a detailed transcript with speaker labels and timestamps.
"""

import json
import re
from datetime import timedelta
from typing import List, Dict, Any
import os

def load_diarization_results(diarization_file: str) -> List[Dict[str, Any]]:
    """Load speaker diarization results from markdown file"""
    with open(diarization_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    diarization_data = []
    
    # Look for the speaker diarization table
    lines = content.split('\n')
    in_table = False
    header_found = False
    
    for line in lines:
        # Look for the start of the speaker diarization table
        if 'Regular Speaker Diarization' in line:
            in_table = True
            header_found = False
            continue
        
        if in_table:
            # Skip header and separator lines
            if line.strip() == '':
                continue
            
            # Check if this is a separator line (contains table formatting)
            if line.startswith('|---'):
                header_found = True
                continue
            
            # Parse table rows - only after we've seen the header separator
            if line.startswith('|') and header_found:
                parts = [part.strip() for part in line.split('|')]
                # Remove empty first and last elements from split
                parts = [part for part in parts if part != '']
                
                if len(parts) >= 4:  # speaker, start, end, duration
                    try:
                        speaker = parts[0]
                        start_time = float(parts[1])
                        end_time = float(parts[2])
                        duration = float(parts[3])
                        
                        diarization_data.append({
                            'speaker': speaker,
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration': duration
                        })
                    except ValueError:
                        # Skip lines that can't be converted to float (like headers)
                        continue
            elif not line.startswith('|'):
                # End of table
                in_table = False
    
    return diarization_data

def load_transcription_results(transcription_file: str) -> List[Dict[str, Any]]:
    """Load transcription results from JSON file"""
    with open(transcription_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('segments', [])

def load_transcription_txt(transcription_txt_file: str) -> str:
    """Load full transcription text from txt file"""
    with open(transcription_txt_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

def map_speakers_to_segments(diarization_data: List[Dict[str, Any]], 
                           transcription_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map speakers to transcription segments based on time overlap with confidence scoring"""
    enhanced_segments = []
    
    for trans_seg in transcription_segments:
        trans_start = trans_seg['start']
        trans_end = trans_seg['end']
        trans_text = trans_seg['text']
        trans_duration = trans_end - trans_start
        
        # Find the speaker that has the most overlap with this segment
        best_overlap = 0
        best_speaker = 'UNKNOWN'
        best_confidence = 0.0
        
        for dia_seg in diarization_data:
            dia_start = dia_seg['start_time']
            dia_end = dia_seg['end_time']
            
            # Calculate overlap between segments
            overlap_start = max(trans_start, dia_start)
            overlap_end = min(trans_end, dia_end)
            overlap_duration = max(0, overlap_end - overlap_start)
            
            if overlap_duration > best_overlap:
                best_overlap = overlap_duration
                best_speaker = dia_seg['speaker']
                # Calculate confidence as ratio of overlap to transcription segment duration
                best_confidence = overlap_duration / trans_duration if trans_duration > 0 else 0.0
        
        # If there's no significant overlap, use the nearest speaker with low confidence
        if best_overlap == 0:
            min_distance = float('inf')
            for dia_seg in diarization_data:
                dia_start = dia_seg['start_time']
                dia_end = dia_seg['end_time']
                
                # Calculate distance to nearest boundary
                distance = min(
                    abs(trans_start - dia_end),
                    abs(trans_end - dia_start),
                    abs(trans_start - dia_start),
                    abs(trans_end - dia_end)
                )
                
                if distance < min_distance:
                    min_distance = distance
                    best_speaker = dia_seg['speaker']
                    best_confidence = 0.1  # Low confidence for distance-based assignment
        
        # Calculate audio quality metrics from transcription
        avg_logprob = trans_seg.get('avg_logprob', 0)
        no_speech_prob = trans_seg.get('no_speech_prob', 0)
        compression_ratio = trans_seg.get('compression_ratio', 1.0)
        
        # Calculate confidence score combining speaker assignment confidence and transcription quality
        # Higher avg_logprob (less negative) = better quality
        # Lower no_speech_prob = better quality
        transcription_quality = max(0.0, min(1.0, (1.0 - no_speech_prob) * (1.0 - abs(avg_logprob) / 10.0)))
        combined_confidence = best_confidence * transcription_quality
        
        enhanced_segments.append({
            'start': trans_start,
            'end': trans_end,
            'text': trans_text,
            'speaker': best_speaker,
            'speaker_confidence': best_confidence,
            'transcription_quality': transcription_quality,
            'combined_confidence': combined_confidence,
            'avg_logprob': avg_logprob,
            'no_speech_prob': no_speech_prob,
            'compression_ratio': compression_ratio
        })
    
    return enhanced_segments

def create_combined_transcript(enhanced_segments: List[Dict[str, Any]], 
                             original_transcript: str,
                             audio_file: str) -> str:
    """Create a combined transcript with speaker labels"""
    transcript_lines = []
    
    # Add header
    from datetime import datetime
    transcript_lines.append(f"# Combined Speaker Diarization and Transcription")
    transcript_lines.append(f"")
    transcript_lines.append(f"**Audio File:** {audio_file}")
    transcript_lines.append(f"**Processing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    transcript_lines.append(f"")
    transcript_lines.append(f"## Full Transcript with Speaker Labels")
    transcript_lines.append(f"")
    
    # Group consecutive segments by same speaker
    current_speaker = None
    current_segments = []
    
    for seg in enhanced_segments:
        if seg['speaker'] != current_speaker:
            # If we have a group of segments, process them
            if current_segments:
                speaker_segments = []
                for s in current_segments:
                    start_time = f"{s['start']:.3f}s"
                    end_time = f"{s['end']:.3f}s"
                    speaker_segments.append(f"[{start_time}-{end_time}] {s['text'].strip()}")
                
                combined_text = " ".join([s['text'].strip() for s in current_segments])
                first_start = f"{current_segments[0]['start']:.3f}s"
                last_end = f"{current_segments[-1]['end']:.3f}s"
                
                transcript_lines.append(f"### {current_segments[0]['speaker']}")
                transcript_lines.append(f"**Time:** [{first_start} - {last_end}]")
                transcript_lines.append(f"")
                transcript_lines.append(f"{combined_text}")
                transcript_lines.append(f"")
            
            current_speaker = seg['speaker']
            current_segments = [seg]
        else:
            current_segments.append(seg)
    
    # Process the last group
    if current_segments:
        speaker_segments = []
        for s in current_segments:
            start_time = f"{s['start']:.3f}s"
            end_time = f"{s['end']:.3f}s"
            speaker_segments.append(f"[{start_time}-{end_time}] {s['text'].strip()}")
        
        combined_text = " ".join([s['text'].strip() for s in current_segments])
        first_start = f"{current_segments[0]['start']:.3f}s"
        last_end = f"{current_segments[-1]['end']:.3f}s"
        
        transcript_lines.append(f"### {current_segments[0]['speaker']}")
        transcript_lines.append(f"**Time:** [{first_start} - {last_end}]")
        transcript_lines.append(f"")
        transcript_lines.append(f"{combined_text}")
        transcript_lines.append(f"")
    
    # Add detailed segment-by-segment breakdown
    transcript_lines.append(f"## Detailed Breakdown by Segments")
    transcript_lines.append(f"")
    
    for seg in enhanced_segments:
        start_time = f"{seg['start']:.3f}s"
        end_time = f"{seg['end']:.3f}s"
        # Include confidence score in detailed view
        confidence_pct = seg['combined_confidence'] * 100
        transcript_lines.append(f"**[{seg['speaker']}] [{start_time} - {end_time}]** {seg['text'].strip()}")
        transcript_lines.append(f"**Confidence:** {confidence_pct:.1f}% | Quality: {seg['transcription_quality']:.2f}")
        transcript_lines.append(f"")
    
    # Calculate speaking time distribution
    speaker_durations = {}
    speaker_segments_count = {}
    speaker_confidence_sums = {}
    
    for seg in enhanced_segments:
        speaker = seg['speaker']
        duration = seg['end'] - seg['start']
        
        if speaker not in speaker_durations:
            speaker_durations[speaker] = 0
            speaker_segments_count[speaker] = 0
            speaker_confidence_sums[speaker] = 0
        
        speaker_durations[speaker] += duration
        speaker_segments_count[speaker] += 1
        speaker_confidence_sums[speaker] += seg['combined_confidence']
    
    # Add speaking time distribution statistics
    transcript_lines.append(f"## Speaking Time Distribution")
    transcript_lines.append(f"")
    
    total_duration = sum(speaker_durations.values())
    for speaker, duration in speaker_durations.items():
        percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
        avg_confidence = speaker_confidence_sums[speaker] / speaker_segments_count[speaker] if speaker_segments_count[speaker] > 0 else 0
        transcript_lines.append(f"### {speaker}")
        transcript_lines.append(f"- **Speaking time:** {duration:.2f}s ({percentage:.1f}% of total)")
        transcript_lines.append(f"- **Segments:** {speaker_segments_count[speaker]}")
        transcript_lines.append(f"- **Average confidence:** {avg_confidence:.3f}")
        transcript_lines.append(f"")
    
    # Add audio quality metrics statistics
    transcript_lines.append(f"## Audio Quality Metrics")
    transcript_lines.append(f"")
    
    avg_logprobs = [seg['avg_logprob'] for seg in enhanced_segments]
    no_speech_probs = [seg['no_speech_prob'] for seg in enhanced_segments]
    compression_ratios = [seg['compression_ratio'] for seg in enhanced_segments]
    
    avg_logprob = sum(avg_logprobs) / len(avg_logprobs) if avg_logprobs else 0
    avg_no_speech_prob = sum(no_speech_probs) / len(no_speech_probs) if no_speech_probs else 0
    avg_compression_ratio = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 1.0
    
    transcript_lines.append(f"- **Average transcription confidence:** {avg_logprob:.3f}")
    transcript_lines.append(f"- **Average no-speech probability:** {avg_no_speech_prob:.3f}")
    transcript_lines.append(f"- **Average compression ratio:** {avg_compression_ratio:.3f}")
    transcript_lines.append(f"")
    
    # Add overall statistics
    speakers = set(seg['speaker'] for seg in enhanced_segments)
    total_duration = sum(seg['end'] - seg['start'] for seg in enhanced_segments)
    
    transcript_lines.append(f"## General Statistics")
    transcript_lines.append(f"- **Total speakers:** {len(speakers)}")
    transcript_lines.append(f"- **Total duration:** {total_duration:.2f}s")
    transcript_lines.append(f"- **Total segments:** {len(enhanced_segments)}")
    transcript_lines.append(f"- **Speakers:** {', '.join(sorted(speakers))}")
    
    return "\n".join(transcript_lines)

def write_combined_results(combined_transcript: str, output_filename: str):
    """Write combined results to a markdown file"""
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(combined_transcript)
    print(f"📄 Combined transcript saved to: {output_filename}")
    return output_filename

def main():
    """Main execution function"""
    print("🎙️  Combining Speaker Diarization and Transcription Results")
    print("="*60)
    
    # Define input files
    diarization_file = "../output/audio_diarization_results.md"
    transcription_json = "../output/audio_transcript.json"
    transcription_txt = "../output/audio_transcript.txt"
    audio_file = "../input/audio.ogg"
    
    # Check if input files exist
    if not os.path.exists(diarization_file):
        print(f"❌ Diarization file '{diarization_file}' not found!")
        print("💡 Please run diarization.py first to generate speaker diarization results")
        return
    
    if not os.path.exists(transcription_json):
        # Try to find the actual transcription file
        import glob
        json_files = glob.glob("../output/*_transcript.json")
        if json_files:
            transcription_json = json_files[0]
            print(f"ℹ️  Using transcription file: {transcription_json}")
        else:
            print(f"❌ Transcription JSON file not found!")
            print("💡 Please run transcription.py first to generate transcript JSON")
            return

    if not os.path.exists(transcription_txt):
        # Try to find the actual transcription text file
        import glob
        txt_files = glob.glob("../output/*_transcript.txt")
        if txt_files:
            transcription_txt = txt_files[0]
            print(f"ℹ️  Using transcription text file: {transcription_txt}")
        else:
            print(f"⚠️  Transcription text file not found, continuing without it")
    
    print(f"📁 Loading diarization results from: {diarization_file}")
    print(f"📁 Loading transcription results from: {transcription_json}")
    
    try:
        # Load data
        diarization_data = load_diarization_results(diarization_file)
        transcription_segments = load_transcription_results(transcription_json)
        
        # Load original transcript text if available
        original_transcript = ""
        if os.path.exists(transcription_txt):
            original_transcript = load_transcription_txt(transcription_txt)
        
        print(f"📊 Diarization segments: {len(diarization_data)}")
        print(f"📊 Transcription segments: {len(transcription_segments)}")
        
        # Map speakers to transcription segments
        print("🔄 Mapping speakers to transcription segments...")
        enhanced_segments = map_speakers_to_segments(diarization_data, transcription_segments)
        
        # Create combined transcript
        print("📝 Creating combined transcript...")
        combined_transcript = create_combined_transcript(
            enhanced_segments, 
            original_transcript, 
            audio_file
        )
        
        # Write results
        output_filename = "../output/audio_combined_transcript.md"
        output_file = write_combined_results(combined_transcript, output_filename)
        
        print(f"✅ Combined transcript created successfully!")
        print(f"📄 Output saved to: {output_file}")
        print(f"📈 Processed {len(enhanced_segments)} segments with speaker labels")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()