import streamlit as st  
import subprocess
import time
import os  
  
def save_uploaded_file(uploaded_file, save_dir):  
    """保存上传的文件到指定目录"""  
    if uploaded_file is not None:  
        # 指定一个保存上传文件的目录  
        if not os.path.exists(save_dir):  
            os.makedirs(save_dir)  
        file_path = os.path.join(save_dir, uploaded_file.name)  
        with open(file_path, 'wb') as f:  
            f.write(uploaded_file.getbuffer())  
        return file_path  

  
def main():  
    st.title("数字人制作")  
  
    # 上传视频文件  
    video = st.file_uploader("上传视频文件", type=["mp4", "avi", "mov", "flv", "mkv", "wmv"])  
    audio = st.file_uploader("上传音频文件", type=["mp3", "wav", "aac", "ogg", "flac", "m4a"])

    btn = st.button("开始处理")
    if btn and video and audio:  
        # 保存上传的视频文件  
        video_path = save_uploaded_file(video, 'target/videos')  
        audio_path = save_uploaded_file(audio, 'target/audios')
        dirname = os.path.basename(video_path)

        output_path = video_path.replace('target', 'result')
        # 命令
        for command in [
            'echo 环境检测：',
            'python -V', 'Scripts\\pip -V',

           ]:
            os.system(command)

        # 构造 ffmpeg 命令：将音频合成到视频中
        ffmpeg_cmd = [
            "ffmpeg", 
            '-y',
            "-i", video_path,  # 输入视频
            "-i", audio_path,  # 输入音频
            "-c:v", "copy",    # 保持原始视频编码
            "-c:a", "aac",     # 使用 aac 编码音频
            "-strict", "experimental", 
            output_path        # 输出路径
        ]

        # 启动命令并实时显示进度
        progress_bar = st.progress(0)  # 初始化进度条
        status_text = st.empty()       # 状态文本
        
        # 运行命令，捕获输出
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                                   encoding='utf-8')

        # 更新进度条
        while True:
            output = process.stdout.readline()
            
            if output == '' and process.poll() is not None:
                break
            
            if output:
                # 在此可以解析 ffmpeg 输出的进度信息
                # ffmpeg 通常会输出形如 'frame=  500 fps=25.0 q=-1.0 size= 1024kB time=00:00:20.00 bitrate= 419.4kbits/s' 的信息
                # 我们可以通过解析 `time` 来估算处理进度
                
                # 示例：假设视频时长是 60 秒，解析 `time` 字段，更新进度
                if "time=" in output:
                    time_str = output.split("time=")[-1].split(" ")[0]
                    h, m, s = time_str.split(":")
                    processed_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    
                    # 假设视频总时长为60秒（可使用 moviepy 等库提取实际时长）
                    total_duration = 60.0
                    
                    progress = processed_seconds / total_duration
                    progress_bar.progress(min(progress, 1.0))  # 更新进度条

                # 在界面上显示当前的执行状态
                status_text.text(f"当前处理状态: {output.strip()}")

        process.wait()  # 等待进程结束
        status_text.text("处理完成！")  # 更新状态
  
        # 使用HTML标签来嵌入视频  
        html_template = f"""  
        <video width="640" height="480" controls>  
            <source src="/{output_path}" type="video/mp4">  
            Your browser does not support the video tag.  
        </video>  
        """  
        video_url = f"/{output_path}"  # 注意：这可能需要你的服务器配置来正确服务静态文件  
  
        # 注意：这里的video_url可能需要根据你的部署环境进行调整  
        # 如果你在本地运行，并且希望直接通过文件路径访问，可能需要一些额外的设置  
        # 比如，在Streamlit中直接通过文件路径访问可能不工作，除非你通过某种方式（如HTTP服务器）来服务这些文件  
  
        # 作为替代方案，你可以直接使用绝对文件路径（但请确保浏览器安全策略允许这样做）  
        # 或者将视频上传到支持HTTP访问的服务器/云服务  
  
        # 这里我们假设你已经在服务器上正确配置了静态文件服务  
        st.write(html_template, unsafe_allow_html=True)  
        with open(output_path, "rb") as file:
            st.download_button(label="下载处理后的视频", data=file, file_name="output_video_with_audio.mp4", mime="video/mp4")

  
if __name__ == "__main__":  
    main()