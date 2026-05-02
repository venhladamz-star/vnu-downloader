import streamlit as st
import os
import subprocess
import glob

st.set_page_config(page_title="VNU Engineering Downloader", page_icon="🚀")
st.title("🌍 Universal Downloader")

OUTPUT_DIR = "temp_downloads"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

url = st.text_input("🔗 Dán link vào đây:", placeholder="https://...")
format_choice = st.radio("Chọn định dạng:", ("🎬 Video MP4", "🎵 Nhạc MP3"))

if st.button("🚀 Bắt đầu tải"):
    if not url:
        st.warning("Vui lòng nhập link!")
    else:
        with st.spinner('Đang xử lý...'):
            try:
                # 1. Dọn dẹp file cũ
                for f in glob.glob(f"{OUTPUT_DIR}/*"):
                    os.remove(f)

                # 2. Cấu hình lệnh yt-dlp
                # Lưu ý: Không để trống bất kỳ phần tử nào trong list cmd
                cmd = [
                    "yt-dlp",
                    "--no-playlist",
                    "--no-check-certificate",
                    "--no-warnings",
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                ]

                # Kiểm tra nếu có file cookies thì mới thêm vào lệnh
                if os.path.exists("cookies.txt"):
                    cmd.extend(["--cookies", "cookies.txt"])

                cmd.extend(["-o", f"{OUTPUT_DIR}/%(title)s.%(ext)s"])

                if format_choice == "🎵 Nhạc MP3":
                    cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
                else:
                    # Fix lỗi 'Format not available' bằng cách chọn định dạng linh hoạt
                    cmd.extend(["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv+ba/b", "--merge-output-format", "mp4"])

                cmd.append(url)

                # 3. Chạy lệnh hệ thống
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

                if result.returncode == 0:
                    files = os.listdir(OUTPUT_DIR)
                    if files:
                        file_path = os.path.join(OUTPUT_DIR, files[0])
                        with open(file_path, "rb") as f:
                            st.success(f"✅ Thành công: {files[0]}")
                            st.download_button(label="⬇️ TẢI VỀ MÁY", data=f, file_name=files[0])
                    else:
                        st.error("Lỗi: Không tìm thấy file sau khi tải.")
                else:
                    st.error("Hệ thống bị chặn hoặc lỗi định dạng.")
                    with st.expander("Chi tiết lỗi"):
                        st.code(result.stderr)

            except Exception as e:
                # Đây là khối lệnh bạn bị thiếu dẫn đến lỗi SyntaxError[cite: 2]
                st.error(f"Lỗi cú pháp hoặc hệ thống: {e}")
