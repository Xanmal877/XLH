import yt_dlp

ydl_opts = {
    'format': 'best',  # This is a placeholder; we will change it later
    'outtmpl': './DownloadedMedia/%(title)s.%(ext)s',
}

def list_formats(url):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        for fmt in formats:
            print(f"{fmt['format_id']}: {fmt['format']} ({fmt.get('ext', 'N/A')})")

def download_video(url, format_id):
    ydl_opts['format'] = format_id
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Download complete for URL:", url)

if __name__ == "__main__":
    url = input("Enter URL: ")
    print("Listing available formats...")
    list_formats(url)
    format_id = input("Enter the format ID you want to download: ")
    download_video(url, format_id)
