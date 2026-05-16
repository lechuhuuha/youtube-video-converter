# 
 
## Description

```
MP3 Convertor Python Script
```

## HOW TO USE

```
- Use Python 3.10 or newer
- Install dependencies: python -m pip install -U -r requirements.txt
- Install Node.js or Deno so yt-dlp can solve YouTube JavaScript challenges
- If your current venv uses Python 3.9, recreate it:
  deactivate
  py -3.14 -m venv .venv314
  .venv314\Scripts\activate
  python --version
  python -m pip install -U -r requirements.txt
- Run the python file "main.py"
- To download online media, paste one or more links when prompted
- Put each link on its own line for bulk downloads
- Duplicate YouTube links with tracking parameters are skipped automatically
- Choose MP3 audio or MP4 video, then choose the download folder
- MP4 downloads prefer high-FPS formats when YouTube provides them
- Restricted YouTube videos may need browser cookies
- To use cookies, export browser cookies to "cookies.txt" and place it beside main.py
- The program does not disable Chrome security settings or read Chrome cookies automatically
- Keep "cookies.txt" private because it contains browser session data
- To convert local files, leave the YouTube prompt blank
- Select MP4 files in bulk
- The program writes each MP3 beside the selected MP4 file
- Online bulk downloads run one at a time with short pauses between requests
- Downloads and conversions run in the background so the progress window stays responsive
- If YouTube still returns HTTP 403, install a yt-dlp PO-token provider:
  https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide
```

##

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/63146468?s=400&u=da361f278311415252978ee270b1d14e3e508c79&v=4" height="128">
  <h2 align="center">Subhadeep Chakraborty</h2>
  <p align="center">
    <a href="https://github.com/SubhadeepZilong">
    	<img src="https://github.com/SubhadeepZilong/Small-Projects/blob/main/Assets/Github_icon.png" alt="Profile" width="40" height="40"/>
    </a>
    <a href="https://twitter.com/subhadeepzilong">
    	<img src="https://github.com/SubhadeepZilong/Small-Projects/blob/main/Assets/twitter_icon.png" alt="Twitter" width="40" height="40"/>
    </a>
    <a href="https://www.linkedin.com/in/subhadeep-chakraborty-b341a8191/">
    	<img src="https://github.com/SubhadeepZilong/Small-Projects/blob/main/Assets/Linkedin_icon.png" alt="Linkedin" width="40" height="40"/>
    </a>
  </p>
</p>

##

## MIT License

Copyright (c) 2022 SubhadeepZilong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

