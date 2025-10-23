# Home Inspector AI - Phase 0 POC

**AI-powered home inspection report generation**

## Overview

This POC validates the core technology: Can we automatically generate professional home inspection reports from audio narration and photos?

### What We're Testing

1. **Audio Transcription**: Convert inspector's verbal narration to text (OpenAI Whisper)
2. **Photo Analysis**: Identify issues in photos (GPT-5 Vision)
3. **Correlation**: Match photos to relevant audio context
4. **Report Generation**: Create professional descriptions

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key (already done)
# .env file contains OPENAI_API_KEY

# Run POC test
python poc/test_pipeline.py
```

## Project Structure

```
home_inspector/
├── .env                    # API keys (DO NOT COMMIT)
├── .env.example           # Template for API keys
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── requirements.txt       # Python dependencies
│
├── poc/                   # Phase 0 POC scripts
│   ├── 1_transcribe.py   # Audio transcription
│   ├── 2_analyze_photos.py # Photo analysis
│   ├── 3_correlate.py    # Audio-photo correlation
│   ├── 4_generate_report.py # Report generation
│   └── test_pipeline.py  # Full end-to-end test
│
├── sample_data/          # Test data for POC
│   ├── audio/           # Sample inspection audio
│   ├── photos/          # Sample inspection photos
│   └── expected/        # Expected output for validation
│
└── outputs/              # Generated results
    ├── transcriptions/
    ├── analyses/
    └── reports/
```

## Phase 0 Goals

**Success Criteria:**
- ✅ Transcription accuracy >85%
- ✅ Photo-audio correlation >80%
- ✅ Generated descriptions are professional quality
- ✅ Full pipeline runs end-to-end
- ✅ Processing time <5 minutes for 45-min inspection

**Timeline:** 2 weeks

## Next Steps After POC

If POC succeeds:
1. Build production backend (FastAPI)
2. Create mobile app (capture interface)
3. Build desktop review app
4. Set up automated testing
5. Deploy to production

## Cost Estimation (POC)

- 10 test inspections @ ~$1.50 each = $15 total
- Proves concept before building full system

## Notes

- This is a PROOF OF CONCEPT
- Not production-ready
- Focus: Validate AI accuracy
- No UI yet, just scripts

## Contact

Questions? See main documentation or reach out to team.
