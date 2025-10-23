# Run POC Test Locally (With Real OpenAI APIs)

Since OpenAI appears to be blocking Claude Code's environment, you can run the full POC test on your own machine where the API key works!

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install openai python-dotenv pillow
```

### Step 2: Update .env with Your API Key

The `.env` file already has your working API key. You're all set!

### Step 3: Generate Synthetic Test Data

```bash
python create_synthetic_data.py
```

This creates:
- Mock audio transcript (simulates Whisper output)
- 3 synthetic inspection photos
- Property info and timestamp mappings

### Step 4: Run POC with REAL APIs

```bash
python run_synthetic_test.py
```

This will:
1. ✅ Load synthetic transcript (skip Whisper to save cost)
2. ✅ Analyze 3 photos with **REAL GPT-4o Vision API**
3. ✅ Correlate photos with audio using **REAL GPT-4o API**
4. ✅ Generate professional report with **REAL GPT-4o API**

**Expected cost:** ~$0.51 per run

## What You'll See

The script will:
- Analyze each photo (shows progress)
- Correlate with audio context (shows confidence scores)
- Generate full inspection report

**Output files:**
```
outputs/analyses/          # Photo analyses
outputs/correlations/      # Photo-audio correlations
outputs/reports/
  ├── inspection_report.json    # Structured data
  └── inspection_report.txt     # Human-readable report
```

## Expected Results

### Success Criteria:
- ✅ All 3 photos analyzed successfully
- ✅ Correlation confidence > 80% average
- ✅ Professional report generated
- ✅ Issues properly categorized by severity

### Sample Output:
```
================================================================================
POC TEST COMPLETE
================================================================================

📊 RESULTS:
   Photos Analyzed: 3
   Correlations Created: 3
   Total Issues Detected: 3
   Overall Condition: Fair (3/5)

🔍 ISSUES BY SEVERITY:
   🚨 Safety Hazard: 1
   ⚠️  Moderate: 1
   📋 Minor: 1

💰 API COSTS:
   Vision Analysis: $0.06
   Correlation: $0.30
   Report Generation: $0.15
   TOTAL: $0.51
```

## View the Report

```bash
cat outputs/reports/inspection_report.txt
```

You'll see a professional inspection report with:
- Executive summary
- Overall condition rating
- Statistics by severity/category
- Detailed findings with recommendations
- Photo references

## Compare with Mock Results

We already ran this with mocked APIs and got 94% correlation confidence.

Now you can validate with **REAL APIs** and see:
- Does GPT-4o Vision accurately describe the photos?
- Does correlation match photo + audio context?
- Is the report professional quality?

## Troubleshooting

**If you get errors:**

1. **"Access denied"** - Even though key works, try:
   ```bash
   pip install --upgrade openai
   ```

2. **"Module not found"** - Install dependencies:
   ```bash
   pip install openai python-dotenv pillow
   ```

3. **"File not found"** - Run from project root:
   ```bash
   cd /path/to/home_inspector
   python run_synthetic_test.py
   ```

## What's Next After Testing?

If the POC shows good results (>80% accuracy):

### Option A: Proceed to Production
- Build FastAPI backend
- Create mobile capture app
- Build desktop review interface
- Deploy to cloud

### Option B: Iterate on POC
- Test with more synthetic scenarios
- Fine-tune prompts
- Optimize costs

---

**Note:** The synthetic data uses simple labeled images. Real inspection photos will provide even better results since GPT-4o Vision excels at analyzing real-world images.

Ready to see the AI in action with real APIs! 🚀
