#!/usr/bin/env python3
"""
Test script for LocalTranscribe v3.1.0 features.

Tests all Phase 1 and Phase 2 enhancements:
- Phase 1: Segment processing and enhanced speaker mapping
- Phase 2: Audio analysis, quality gates, enhanced proofreading
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from localtranscribe.pipeline import PipelineOrchestrator

def main():
    print("=" * 80)
    print("LocalTranscribe v3.1.0 - Full Feature Test")
    print("=" * 80)
    print()

    # Configuration
    audio_file = Path("input/20251030_Coaching_Session_4.ogg")
    output_dir = Path("output/test_v3_1")
    quality_report_path = output_dir / "quality_report.txt"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Audio File: {audio_file}")
    print(f"Output Dir: {output_dir}")
    print(f"Quality Report: {quality_report_path}")
    print()

    # Get HuggingFace token from environment
    from dotenv import load_dotenv
    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_TOKEN")

    if not hf_token:
        print("⚠️  Warning: HUGGINGFACE_TOKEN not found in environment")
        print("    Diarization may fail without token")
        print()

    print("=" * 80)
    print("Pipeline Configuration - ALL v3.1 Features Enabled")
    print("=" * 80)
    print()

    print("✅ Phase 1 Features:")
    print("   - Segment Post-Processing: ENABLED")
    print("   - Enhanced Speaker Mapping: ENABLED")
    print("   - Speaker Region Analysis: ENABLED")
    print()

    print("✅ Phase 2 Features:")
    print("   - Audio Quality Analysis: ENABLED")
    print("   - Quality Gates (per-stage): ENABLED")
    print("   - Domain Dictionaries: ENABLED (technical, business, common)")
    print("   - Acronym Expansion: ENABLED")
    print("   - Quality Report Generation: ENABLED")
    print()

    print("=" * 80)
    print("Starting Pipeline...")
    print("=" * 80)
    print()

    start_time = datetime.now()

    try:
        # Create pipeline with all v3.1 features enabled
        pipeline = PipelineOrchestrator(
            audio_file=audio_file,
            output_dir=output_dir,
            hf_token=hf_token,

            # Model settings
            model_size="medium",  # v3.0 default
            implementation="auto",

            # Phase 1: Segment Processing (Default: enabled)
            enable_segment_processing=True,
            use_speaker_regions=True,

            # Phase 2: Audio Analysis
            enable_audio_analysis=True,

            # Phase 2: Quality Gates
            enable_quality_gates=True,
            quality_report_path=quality_report_path,

            # Phase 2: Enhanced Proofreading
            enable_proofreading=True,
            proofreading_domains=["technical", "business", "common"],
            enable_acronym_expansion=True,

            # Output
            output_formats=["txt", "json", "md"],

            # Verbose logging
            verbose=True
        )

        # Run the pipeline
        print("🚀 Executing pipeline with all v3.1 enhancements...\n")
        result = pipeline.run()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print()
        print("=" * 80)
        print("Pipeline Execution Complete!")
        print("=" * 80)
        print()

        if result.success:
            print("✅ Status: SUCCESS")
            print()
            print(f"⏱️  Total Processing Time: {duration:.1f}s")
            print(f"🎤 Speakers Detected: {result.num_speakers}")
            print(f"📝 Total Segments: {len(result.segments)}")
            print(f"📄 Transcript Length: {len(result.transcript)} characters")
            print()

            print("📁 Output Files:")
            for format_name, file_path in result.output_files.items():
                file_size = file_path.stat().st_size if file_path.exists() else 0
                print(f"   - {format_name.upper()}: {file_path.name} ({file_size:,} bytes)")

            if quality_report_path.exists():
                report_size = quality_report_path.stat().st_size
                print(f"   - QUALITY REPORT: {quality_report_path.name} ({report_size:,} bytes)")
            print()

            # Display quality report if available
            if quality_report_path.exists():
                print("=" * 80)
                print("Quality Report Summary")
                print("=" * 80)
                print()

                with open(quality_report_path, "r") as f:
                    report = f.read()
                    # Show first 2000 characters of report
                    if len(report) > 2000:
                        print(report[:2000])
                        print(f"\n... (truncated, full report in {quality_report_path.name})")
                    else:
                        print(report)
                print()

            # Show sample of transcript
            print("=" * 80)
            print("Transcript Sample (first 500 characters)")
            print("=" * 80)
            print()
            print(result.transcript[:500])
            if len(result.transcript) > 500:
                print("\n... (truncated)")
            print()

            print("=" * 80)
            print("✅ Test Complete - All v3.1 Features Executed Successfully!")
            print("=" * 80)
            print()
            print(f"📂 Full results saved to: {output_dir}")
            print(f"📊 Quality report: {quality_report_path}")

        else:
            print("❌ Status: FAILED")
            print(f"Error: {result.error_message}")
            return 1

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ Pipeline Execution Failed")
        print("=" * 80)
        print()
        print(f"Error: {type(e).__name__}: {str(e)}")

        import traceback
        print()
        print("Traceback:")
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
