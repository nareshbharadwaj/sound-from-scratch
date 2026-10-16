# Lesson pages

Interactive lessons and tools, published as artifacts. Edit the HTML here,
then republish to the same URL so links in the notes keep working.

| File | Published at | What it is |
| --- | --- | --- |
| `lesson-01-sampling.html` | https://claude.ai/artifact/CTMTE6mSumB1BdVKi4vxHA | Lesson 1: how sound becomes numbers, step by step |
| `lesson-02-fourier.html` | https://claude.ai/artifact/EWputRnDr8NPzdmsmFoS33 | Lesson 2: the Fourier transform, from adding sines to the FFT |
| `code-02-fourier.html` | https://claude.ai/artifact/HFZXH3YnELwbHHyHsFPE65 | Lesson 2's code, read line by line, with real outputs. Built by `src/build_code_02.py` |
| `lesson-03-stft.html` | https://claude.ai/artifact/Q6vLsTectqLmXyoiAUJ1yZ | Lesson 3: windows, the STFT and spectrograms, ending with a real voice. Built by `src/build_lesson_03.py` (embeds the clip in `src/assets/`) |
| `code-03-stft.html` | https://claude.ai/artifact/C9tFogjcM8wvoDmc67rPef | Lesson 3's code, read line by line, with real outputs. Built by `src/build_code_03.py` |
| `aliasing-lab.html` | https://claude.ai/artifact/HNEgSgSjcnwo9fAVQivseJ | Playground for lesson 1: any tone at any sample rate |

The plan itself is at https://claude.ai/artifact/ExAUhat1xmLmzwM5tV3ZCE.

Pages with a template in `src/` are generated: edit the template, run its
build script from the repo root, then republish. Code pages share
`src/codepage.py` and `src/code-page.css`.
