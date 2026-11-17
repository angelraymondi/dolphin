import httpx
from pathlib import Path

def fetch_video(video_url, filename):
  dir = Path(__file__).resolve().parent.parent / "downloads"
  dir.mkdir(parents=True, exist_ok=True)
  
  file_path = dir / filename
  
  if file_path.exists():
    print(f"Error: {file_path} already exists")
    return None

  try:
    with httpx.stream("GET", video_url, timeout=15.0) as response:
      response.raise_for_status()
      
      with open(file_path, "wb") as file:
          for chunk in response.iter_bytes(chunk_size=8192):
            file.write(chunk)
    
    return None
  except httpx.HTTPError as e:
    print(f"An error ocurred: {e}")
    return None
