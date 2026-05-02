import streamlit as st
import os
import subprocess
import glob

st.set_page_config(page_title="VNU Engineering Downloader", page_icon="🚀")
st.title("🌍 Universal Downloader")

# Thư mục tạm
OUTPUT_DIR = "temp_downloads"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

url = st.text_input("🔗 Dán link vào đây:", placeholder="https://www.youtube.com/watch?v=...")
format_choice = st.radio("Chọn định dạng:", ("🎬 Video MP4", "🎵 Nhạc MP3"))

if st.button("🚀 Bắt đầu tải"):
    if not url:
        st.warning("Vui lòng nhập link!")
    else:
        with st.spinner('Đang thực thi các bước vượt rào cản hệ thống...'):
            try:
                # Dọn dẹp file cũ
                for f in glob.glob(f"{OUTPUT_DIR}/*"):
                    os.remove(f)

                # Lệnh yt-dlp với cấu hình chống lỗi 403
                cmd = [
                    "yt-dlp",
                    "--no-playlist",
                    "--no-check-certificate",
                    "--no-warnings",
                    # Giả lập trình duyệt Chrome thật trên Windows
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "--add-header", "Accept-Language: vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                    "--add-header", "Sec-Ch-Ua-Platform: Windows",
                    "-o", f"{OUTPUT_DIR}/%(title)s.%(ext)s"
                ]

                if format_choice == "🎵 Nhạc MP3":
                    cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
                else:
                    # Lấy mp4 có sẵn để tránh render nặng làm server bị sập[cite: 2]
                    cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])

                cmd.append(url)

                # Chạy lệnh
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

                if result.returncode == 0:
                    files = os.listdir(OUTPUT_DIR)
                    if files:
                        file_path = os.path.join(OUTPUT_DIR, files[0])
                        with open(file_path, "rb") as f:
                            st.success(f"✅ Thành công: {files[0]}")
                            st.download_button(label="⬇️ TẢI VỀ MÁY", data=f, file_name=files[0])
                else:
                    st.error("Lỗi 403: YouTube đã chặn IP của server này.")
                    with st.expander("Chi tiết lỗi"):
                        st.code(result.stderr)

            except Exception as e:
                st.error(f"Lỗi: {e}")
