import sys, os, time
import console_control as console
import main_functions as core

# Checking if ffmpeg.exe and ffprobe.exe are in the bin folder
if not os.path.exists("./bin/ffmpeg.exe") or not os.path.exists("./bin/ffprobe.exe"):
    console.write("Please place ffmpeg.exe and ffprobe in the /bin folder... Exiting...")
    time.sleep(5)
    exit()

init_time = time.time()
argv = sys.argv
total_MBs_saved = 0.0
search_folder = "."
output_folder = "./compressed"

if len(argv) > 1:
    if os.path.exists(argv[1]):
        search_folder = argv[1]

if len(argv) > 2:
    if os.path.exists(argv[2]):
        output_folder = argv[2]
        
console.clean_upper_line()
mp4_files = core.find_mp4_files(search_folder)

console.write("- - - -  VIDEO COMPRESSOR  - - - -")
console.write(f"Search Folder: {os.path.abspath(search_folder)}")
console.write(f"Output Folder: {os.path.abspath(output_folder)}")
console.write(f"Files Found: {len(mp4_files)}")
console.write("- - - - - - - - - - - - - - - - - -")

crf = console.ask_number("Select CRF amount")
preset = console.ask_number("Select Preset. 1=slow 2=medium 3=fast")
encoder = console.ask_number("Select Encode. 1=libx265 2=hevc_nvenc")

match preset:
    case 1:
        preset = "slow"
    case 2:
        preset = "medium"
    case 3:
        preset = "fast"

match encoder:
    case 1:
        encoder = "libx265"
    case 2:
        encoder = "hevc_nvenc"

console.write(f"CRF: {crf}")
console.write(f"Preset: {preset}")
console.write("- - - - - - - - - - - - - - - - - -")

for file in mp4_files:
    file = os.path.abspath(file)
    output_file = output_folder + "/" + os.path.basename(file)
    file_duration = core.get_mp4_duration(file)
    file_size_MB = core.cut_number(os.path.getsize(file) / (1024 * 1024), 3)
    
    console.write(f"MP4 Path: {file}")
    console.write(f"Duration: {file_duration}")
    console.write(f"Original Size: {file_size_MB} MB")
    console.write(f"Compressed Path: {output_file}")
    
    thread, state = core.compress_async(
        input_path=file,
        output_path=output_file,
        crf=crf,
        encoder=encoder,
        preset=preset
    )
    
    while state["finished"] == False:
        console.write(f"Compressed Time: {core.hhmmss(state["seconds_processed"])}")
        time.sleep(0.5)
        console.clean_upper_line()
    
    compressed_file_size_MB = core.cut_number(os.path.getsize(output_file) / (1024 * 1024), 3)
    saved_MB = file_size_MB - compressed_file_size_MB
    total_MBs_saved = total_MBs_saved + saved_MB
    
    console.clean_upper_line()
    console.clean_upper_line()
    console.clean_upper_line()
    console.clean_upper_line()
    
    console.write(f"File: {os.path.basename(output_file)}")
    console.write(f"Saved MBs: {saved_MB} MBs")
    console.write("- - - - - - - - - - - - - - - - - -")

console.write(f"Finished compression of {len(mp4_files)} files...")
console.write(f"Total space saved: {total_MBs_saved}MB")
console.write(f"Total Runtime: {time.time() - init_time}")

input("Press enter to close...")