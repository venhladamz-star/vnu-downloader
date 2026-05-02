import streamlit as st
import os
import subprocess
import glob

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="VNU Engineering Downloader", page_icon="🚀")
st.title("🌍 Universal Downloader")
st.markdown("---")

# Thư mục tạm lưu file trên server
OUTPUT_DIR = "temp_downloads"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- KIỂM TRA HỆ THỐNG ---
if os.path.exists("cookies.txt"):
    st.sidebar.success("✅ Đã nhận file cookies.txt")
else:
    st.sidebar.warning("⚠️ Thiếu cookies.txt (Có thể bị lỗi 403 với YouTube)")

# --- GIAO DIỆN NGƯỜI DÙNG ---
url = st.text_input("🔗 Dán link video/nhạc vào đây:", placeholder="https://www.youtube.com/watch?v=...")
format_choice = st.radio("Chọn định dạng đầu ra:", ("🎬 Video MP4", "🎵 Nhạc MP3"))

if st.button("🚀 Bắt đầu xử lý"):
    if not url:
        st.warning("Bạn chưa nhập đường dẫn!")
    else:
        with st.spinner('Đang thực thi các bước vượt rào cản hệ thống...'):
            try:
                # 1. Dọn dẹp file cũ trong thư mục tạm
                for f in glob.glob(f"{OUTPUT_DIR}/*"):
                    try: os.remove(f)
                    except: pass

                # 2. Cấu hình lệnh yt-dlp
                cmd = [
                    "yt-dlp",
                    "--no-playlist",
                    "--no-check-certificate",
                    "--no-warnings",
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "--add-header", "Accept-Language: vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                ]

                # Tự động dùng cookies nếu có
                if os.path.exists("cookies.txt"):
                    cmd.extend(["--cookies", "cookies.txt"])

                # Cấu hình đường dẫn đầu ra
                cmd.extend(["-o", f"{OUTPUT_DIR}/%(title)s.%(ext)s"])

                if format_choice == "🎵 Nhạc MP3":
                    # Trích xuất âm thanh chất lượng cao
                    cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
                else:
                    # Sửa lỗi 'Requested format is not available' bằng cách ưu tiên MP4 linh hoạt
                    cmd.extend([
                        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv+ba/b",
                        "--merge-output-format", "mp4"
                    ])

                # Tham số cuối cùng luôn là URL[cite: 2]
                cmd.append(url)

                # 3. Chạy lệnh hệ thống
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

                if result.returncode == 0:
                    downloaded_files = os.listdir(OUTPUT_DIR)
                    if downloaded_files:
                        file_path = os.path.join(OUTPUT_DIR, downloaded_files[0])
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                            st.success(f"✨ Xử lý thành công: {downloaded_files[0]}")
                            st.download_button(
                                label="⬇️ NHẤN VÀO ĐÂY ĐỂ TẢI VỀ MÁY",
                                data=file_data,
                                file_name=downloaded_files[0],
                                mime="application/octet-stream"
                            )
                    else:
                        st.error("Lỗi: Không tìm thấy file sau khi tải xuống.")
                else:
                    st.error("❌ Hệ thống gặp sự cố (Có thể do IP bị chặn hoặc Link lỗi).")
                    with st.expander("Xem chi tiết lỗi kỹ thuật"):
                        st.code(result.stderr)

            except Exception as e:
                # Khối lệnh xử lý ngoại lệ để tránh lỗi SyntaxError[cite: 2]
                st.error(f"Đã xảy ra sự cố ngoài ý muốn: {str(e)}")

st.markdown("---")
st.caption("Ứng dụng dành cho bạn bè & người thân | Vũ Bảo Khuê - VNU UET")
