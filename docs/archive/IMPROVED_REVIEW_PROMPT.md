# Improved Prompt for Pipeline Usability Review

## Direct Usage Prompt

```
You are a senior software engineer with 10+ years of experience and a former technical founder who has shipped production ML/AI tools. Review the LocalTranscribe pipeline for usability improvements.

## Project Context
LocalTranscribe is an alpha-stage CLI tool for offline audio transcription with speaker diarization, optimized for Apple Silicon (M4 Pro). It consists of a 3-step pipeline:
1. **diarization.py** - Speaker identification using pyannote-audio
2. **transcription.py** - Speech-to-text using Whisper (MLX/Faster/Original)
3. **combine.py** - Merges results into speaker-labeled transcripts

## Your Task
Conduct a comprehensive usability review using sequential thinking and Context7 for library documentation.

### Files to Analyze
**Core Pipeline:**
- `/scripts/diarization.py` (306 lines)
- `/scripts/transcription.py` (463 lines)
- `/scripts/combine.py` (385 lines)

**Documentation:**
- `/README.md`
- `/docs/INSTALLATION.md`
- `/docs/USAGE.md`
- `/docs/CONFIGURATION.md`
- `/docs/TROUBLESHOOTING.md`

**Configuration:**
- `/requirements.txt`
- `/.env.example`

### Research Required (use Context7)
1. **mlx-whisper** - Apple Silicon optimization patterns
2. **faster-whisper** - Performance tuning options
3. **openai-whisper** - Best practices
4. **pyannote-audio** - Configuration and optimization
5. **torch/torchaudio** - MPS backend best practices
6. **Click or Typer** - Modern CLI framework patterns
7. **rich** - Terminal UI improvements

### Known Pain Points to Address
1. **Hardcoded file paths**: `audio_file = "../input/audio.ogg"` (lines 259, 313, 410)
2. **No CLI arguments**: Users must edit source code to change files
3. **No batch processing**: One file at a time only
4. **Manual file placement**: Files must be renamed and moved manually
5. **Hardcoded parameters**: Model size, speaker count, language settings in code
6. **Limited error recovery**: Pipeline stops on first error
7. **Generic speaker labels**: SPEAKER_00, SPEAKER_01 with no customization

### Analysis Framework

#### 1. Installation Experience (15 minutes)
- Evaluate time-to-first-success
- Identify dependency pain points
- Consider containerization opportunities
- **Output**: Quick wins for easier setup

#### 2. Core Workflow (30 minutes)
- Analyze 3-step pipeline execution
- Review inter-script communication (file I/O)
- Assess error handling at boundaries
- Evaluate automation opportunities
- **Output**: Workflow streamlining recommendations

#### 3. Configuration & Flexibility (20 minutes)
- Map hardcoded values to configurable parameters
- Design configuration file structure (YAML/TOML)
- Propose CLI argument schema
- **Output**: Configuration system design

#### 4. Error Handling & DX (15 minutes)
- Review error messages for actionability
- Assess debugging capabilities
- Evaluate implementation fallback chains
- **Output**: Error handling improvements

#### 5. User Interface (15 minutes)
- Evaluate console output clarity
- Review progress indication
- Consider modern CLI patterns (rich, typer)
- **Output**: UI/UX enhancement proposals

#### 6. Architecture (20 minutes)
- Assess code organization and modularity
- Review data flow between scripts
- Identify refactoring opportunities
- **Output**: Architecture recommendations

### Deliverables

Create `/docs/USABILITY_REVIEW.md` with:

#### Executive Summary (3-5 paragraphs)
- Current state assessment
- Top 5 priority improvements
- Estimated impact statements
- Quick wins vs. longer-term investments

#### Critical Issues
For each issue:
```markdown
### Issue: [Brief Title]
**Severity**: Critical | Major | Minor
**User Impact**: [Who is affected, how often, what's the pain]
**Current Behavior**: [Code reference with file:line]
**Recommended Solution**: [Specific approach]
**Implementation Complexity**: [Hours/Days estimate]
**Example Code**: [Working implementation]
```

#### Prioritized Roadmap

**Phase 1: Quick Wins (1-2 weeks)**
- [ ] CLI argument parsing (argparse/Click/Typer)
- [ ] Configuration file support (YAML/TOML)
- [ ] Better error messages with recovery suggestions
- [ ] Remove hardcoded paths

**Phase 2: Core UX (3-4 weeks)**
- [ ] Batch processing support
- [ ] Custom speaker labels
- [ ] Pipeline automation (single command)
- [ ] Progress bars and status updates

**Phase 3: Advanced Features (4-8 weeks)**
- [ ] Watch mode for new files
- [ ] Real-time processing
- [ ] Plugin system for output formats
- [ ] Optional web UI

**Phase 4: Production Hardening**
- [ ] Comprehensive test suite
- [ ] Performance benchmarks
- [ ] CI/CD pipeline
- [ ] Package distribution (pip/brew)

#### Code Examples
For top 3 recommendations, provide:
1. **Current implementation** (actual code)
2. **Proposed implementation** (working code)
3. **Migration notes**
4. **Testing approach**

#### Success Metrics
Define measurable improvements:
- Time-to-first-success: [Current] → [Target]
- Steps for basic workflow: [Current] → [Target]
- Lines of config needed: [Current] → [Target]
- Common errors encountered: [Current] → [Target]

### Implementation Examples to Create

**1. `/docs/examples/cli_interface.py`**
Complete CLI implementation using Click or Typer with:
- File path arguments
- Model size selection
- Speaker count configuration
- Output format choices
- Verbose/debug modes

**2. `/docs/examples/config.yaml`**
Configuration file with:
- Input/output directories
- Model settings
- Speaker detection parameters
- Performance tuning options
- Output format preferences

**3. `/docs/examples/batch_processor.py`**
Batch processing script showing:
- Directory scanning
- Progress tracking
- Error handling per file
- Results aggregation
- Logging configuration

**4. `/docs/examples/pipeline_orchestrator.py`**
Unified pipeline runner:
- Single command execution
- Automatic dependency checking
- State management
- Resume from failure
- Output validation

### Guidelines

**DO:**
✅ Use specific code references (file:line)
✅ Provide working code examples
✅ Reference library docs from Context7
✅ Apply sequential thinking for complex analysis
✅ Consider backward compatibility
✅ Estimate implementation effort
✅ Suggest incremental improvements

**DON'T:**
❌ Suggest complete rewrites
❌ Add unnecessary dependencies
❌ Ignore performance implications
❌ Break offline capability
❌ Propose solutions without examples
❌ Forget the alpha stage context

### Sequential Thinking Application

Use `mcp__sequential-thinking-server__sequentialthinking` to:

1. **User Journey Analysis**
   - Map step-by-step experience from git clone to final output
   - Identify friction at each transition point
   - Calculate cumulative time and frustration

2. **Alternative Evaluation**
   - For each recommendation, consider 2-3 implementation approaches
   - Weigh pros/cons of each
   - Justify final recommendation

3. **Dependency Analysis**
   - Map relationships between improvements
   - Identify which changes enable others
   - Create dependency-aware roadmap

4. **Risk Assessment**
   - Consider breaking changes
   - Evaluate migration complexity
   - Plan for backward compatibility

### Target User Personas

Consider these users in your analysis:

**1. Researcher (30% of users)**
- Transcribing interviews, focus groups
- Needs accuracy > speed
- Limited technical expertise
- Values: Simplicity, reliability, output quality

**2. Content Creator (40% of users)**
- Podcasters, YouTubers
- Needs speed > perfect accuracy
- Moderate technical skills
- Values: Batch processing, automation, format flexibility

**3. Developer (20% of users)**
- Integrating into larger workflows
- Needs programmatic control
- High technical expertise
- Values: API, extensibility, performance

**4. Business User (10% of users)**
- Meeting transcription, call notes
- Needs ease-of-use
- Low technical expertise
- Values: GUI, simplicity, templates

### Competitive Analysis

Compare against (features, not specifics):
- **OpenAI Whisper API**: Developer experience, API design
- **AssemblyAI**: Configuration flexibility, output formats
- **Otter.ai**: User experience, simplicity
- **Descript**: Integration, workflow automation

Maintain differentiators:
✅ 100% offline/local processing
✅ Apple Silicon optimization
✅ No recurring costs
✅ Full data privacy

### Output Format Requirements

```markdown
# LocalTranscribe Usability Review

**Date**: [YYYY-MM-DD]
**Reviewer**: [Senior Software Engineer & Former Founder]
**Project Version**: Alpha
**Review Scope**: Full pipeline (installation → output)

## Executive Summary
[3-5 paragraphs with key findings]

## Critical Issues
[Detailed analysis with code examples]

## Major Usability Issues
[Prioritized list with solutions]

## Minor Improvements
[Quick wins and polish items]

## Architecture Recommendations
[Long-term structural improvements]

## Prioritized Action Plan
[Phased roadmap with dependencies]

## Code Examples
[Working implementations for top recommendations]

## Success Metrics
[Measurable improvement targets]

## Appendix: Research Notes
[Context7 findings and library best practices]
```

---

**Execute this review now, producing `/docs/USABILITY_REVIEW.md` and example files in `/docs/examples/`.**

Use sequential thinking throughout and reference Context7 documentation for all major libraries. Focus on actionable, specific recommendations with working code examples.
```

## Why This Prompt is Better

### Improvements Over Original

1. **Specific Context**: References actual file paths, line numbers, and known pain points from your codebase

2. **Structured Approach**: Breaks down the 2-hour review into timed segments with clear objectives

3. **Actionable Output**: Requires working code examples, not just descriptions

4. **Tool Integration**: Explicitly calls for Context7 usage for library research and sequential thinking for complex analysis

5. **Measurable Goals**: Defines success metrics and improvement targets

6. **User-Centric**: Includes persona analysis to guide recommendations

7. **Phased Roadmap**: Organizes improvements from quick wins to long-term investments

8. **Risk-Aware**: Considers backward compatibility and migration complexity

9. **Example-Driven**: Requires creation of working implementation examples

10. **Competitive Context**: Frames recommendations against industry alternatives while preserving differentiators

### Key Additions

**Quantified Scope**: Specific file counts, line numbers, and time estimates

**Research Requirements**: Exact libraries to investigate with Context7

**Template Structure**: Markdown template showing expected output format

**Code-First**: Emphasis on working examples over theoretical suggestions

**Persona-Driven**: Analysis through lens of 4 distinct user types

**Dependencies**: Explicit consideration of improvement ordering

## Usage

Simply copy the content from the code block above and use it as your prompt. It incorporates all the context from your repository and provides clear execution instructions.
